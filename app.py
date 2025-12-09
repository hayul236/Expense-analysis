from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret"

# --- DATABASE SETUP ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
conn.commit()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        flash("Username already exists!", "error")
        return redirect(url_for('index', show_register='1'))

    
    c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
    conn.commit()
    flash("Registration successful! Please log in.","success")
    return redirect(url_for('index', show_register='1'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    user = c.fetchone()
    if user:
        session['user'] = username
        return redirect(url_for('home'))
    
    flash("Invalid username or password", "login-error")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('home.html', user=session['user'])

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'user' not in session:
        return jsonify({'error': 'not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400

    f = request.files['file']
    filename = secure_filename(f.filename)
    if filename == '':
        return jsonify({'error': 'empty filename'}), 400

    # Read file with pandas. Try excel first, then csv.
    try:
        # If it's an excel file, use read_excel
        if filename.lower().endswith(('.xls', '.xlsx', '.xlsm', '.xlsb')):
            df = pd.read_excel(f, header = 0) # first row header 0, so based on sequence of headers, not by column names
        else:
            # fallback to csv (read from stream)
            f.stream.seek(0)
            df = pd.read_csv(f, header = 0)
            
                # Calculate total spent per row using column indexes
        df['Total'] = df.iloc[:, 2] * df.iloc[:, 3]  # unit price * quantity

        # Group by date (column 0)
        summary = df.groupby(df.iloc[:, 0])['Total'].sum().reset_index()
        summary.iloc[:, 0] = pd.to_datetime(summary.iloc[:, 0], errors='coerce')
        summary.sort_values(by=summary.columns[0], inplace=True)
        summary.iloc[:, 0] = summary.iloc[:, 0].dt.strftime('%d/%m/%Y')
        # Convert to JSON for frontend chart
        chart_data = {
            'dates': summary.iloc[:, 0].astype(str).tolist(),
            'totals': summary['Total'].tolist()
        }
        # ANALYSIS
        # Highest spending date
        highest_idx = summary['Total'].idxmax()
        highest_date = summary.iloc[highest_idx, 0].strftime('%d/%m/%Y')
        
        highest_products_df = df[df.iloc[:, 0] == pd.to_datetime(summary.iloc[highest_idx, 0], dayfirst=True)]
        highest_products = list(zip(highest_products_df.iloc[:, 1], highest_products_df.iloc[:, 3]))

        # Lowest spending date
        lowest_idx = summary['Total'].idxmin()
        lowest_date = summary.iloc[lowest_idx, 0].strftime('%d/%m/%Y')
        
        lowest_products_df = df[df.iloc[:, 0] == pd.to_datetime(summary.iloc[lowest_idx, 0], dayfirst=True)]
        lowest_products = list(zip(lowest_products_df.iloc[:, 1], lowest_products_df.iloc[:, 3]))

        # Average daily spending (assume 30 days in the month)
        average_spent = round(summary['Total'].sum() / 30, 2)

        analysis = {
            'highest': {'date': highest_date, 'products': highest_products},
            'lowest': {'date': lowest_date, 'products': lowest_products},
            'average': average_spent
        }

        return jsonify({'success': True, 'rows': len(df), 'chart_data': chart_data, 'analysis': analysis})

    
    except Exception as e:
        return jsonify({'error': 'failed to read file', 'details': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
