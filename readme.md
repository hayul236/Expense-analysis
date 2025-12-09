dashboard_project/
│
├─ app.py                  # Flask backend (handles login, register, Excel upload)
├─ users.db                # SQLite database (auto-created by app.py)
│
├─ templates/              # HTML files
│   ├─ index.html          # Login page
│   └─ home.html           # Dashboard page (welcome + Excel + chart + analysis)
│
├─ static/                 # CSS, JS, and any icons/images
│   ├─ style.css          
│   ├─ script-home.js
│   └─ script-index.js           # JS for Excel upload, chart rendering
│
├─ uploads/                # (Optional) store uploaded Excel files
│
└─ requirements.txt        # Python packages: Flask, pandas, openpyxl, etc.