const expenseChartCanvas = document.getElementById("expenseChart");

if (!expenseChartCanvas) {
    console.warn("No chart canvas found on this page, skipping chart code.");
} 
else {
    const insertBtn = document.getElementById("insertBtn");
    const excelInput = document.getElementById("excelInput");
    const fileNameDiv = document.getElementById("fileName");
    let expenseChart = null;

    insertBtn.addEventListener("click", e => {
        e.preventDefault();
        excelInput.click();
    });

    excelInput.addEventListener("change", () => {
        if (!excelInput.files[0]) return;
        fileNameDiv.textContent = excelInput.files[0].name;

        const formData = new FormData();
        formData.append("file", excelInput.files[0]);

        fetch("/upload_excel", { method: "POST", body: formData })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                if (data.success) {
                    alert(`Upload successful! ${data.rows} rows loaded.`);

                    const labels = data.chart_data.dates;
                    const ctx = expenseChartCanvas.getContext("2d");
                    if (expenseChart) expenseChart.destroy();

                    expenseChart = new Chart(ctx, {
                        type: "line",
                        data: {
                            labels: labels,
                            datasets: [{
                                label: "Total Spent ($)",
                                data: data.chart_data.totals,
                                borderColor: "#008B8B",
                                backgroundColor: "rgba(0,139,139,0.2)",
                                fill: true,
                                tension: 0.3
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: true },
                                tooltip: { mode: 'index', intersect: false }
                            },
                            scales: {
                                x: { type: 'category',
                                    title: { display: true, text: 'Date' } },
                                y: { title: { display: true, text: 'Total Spent ($)' }, beginAtZero: true }
                            }
                        }
                    });
                    document.getElementById("highestSpending").textContent = 
                    `Highest spending date: ${data.analysis.highest.date} (Products: ${data.analysis.highest.products.map(p => `${p[0]} :${p[1]}`).join(", ")})`;
                    document.getElementById("lowestSpending").textContent = 
                    `Lowest spending date: ${data.analysis.lowest.date} (Products: ${data.analysis.lowest.products.map(p => `${p[0]} :${p[1]}`).join(", ")})`;
                    document.getElementById("averageSpending").textContent = `Average day spending in the month: $${data.analysis.average.toFixed(2)}`;
                } else {
                    alert("Upload failed: " + (data.error || "Unknown error"));
                }
            })
            .catch(err => { console.error(err); alert("Something went wrong."); });
    });
}