# Sales Data Analysis System (Flask)

A beginner-friendly web application to import sales CSV files, validate rows, calculate revenue and quantity, rank products, and visualize monthly revenue.

## Features
- Flask frontend with Dashboard, CSV Import, and Sales Records pages.
- CSV header and row validation with downloadable error report.
- Revenue = `quantity × unit_price`.
- Product-wise quantity and revenue ranking.
- Monthly revenue trend chart generated with Matplotlib.
- Pandas-based grouping and aggregation. NumPy is included for future numeric analysis.
- SQLAlchemy database models for `products` and `sales`.
- Duplicate policy: an identical normalized row (product, category, date, quantity, unit price, region) is skipped using a SHA-256 fingerprint. Different sales with any changed field are retained.
- SQLite works immediately. MySQL can be enabled by changing `DATABASE_URL`.

## Project structure
```text
sales_data_analysis_flask/
├── app.py
├── models.py
├── requirements.txt
├── .env.example
├── README.md
├── services/
│   ├── __init__.py
│   ├── csv_service.py
│   └── analytics.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── upload.html
│   └── sales.html
├── static/css/style.css
├── sample_data/sample_sales.csv
└── tests/
    ├── conftest.py
    └── test_app.py
```

## Requirements
- Python 3.10 or newer
- Windows, macOS, or Linux
- MySQL is optional; SQLite is the default.

## Run on Windows (PowerShell)
Open PowerShell in the extracted project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

If PowerShell blocks activation, use this command for the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or skip activation and run `.venv\\Scripts\\python.exe -m pip install -r requirements.txt` followed by `.venv\\Scripts\\python.exe app.py`.

Open http://127.0.0.1:5000 in your browser. Choose **Import CSV** and upload `sample_data/sample_sales.csv`.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## MySQL setup (optional)
1. Create a database in MySQL:
   ```sql
   CREATE DATABASE sales_analysis CHARACTER SET utf8mb4;
   ```
2. Edit `.env` and set:
   ```text
   DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost/sales_analysis
   ```
3. Restart the app. SQLAlchemy creates the `products` and `sales` tables automatically.

The schema corresponds to:
- `products(product_id, product_name, category)`
- `sales(sale_id, product_id, sale_date, quantity, unit_price, region, sale_hash, created_at)`

The extra `sale_hash` field enforces the duplicate-import policy.

## CSV format
Required columns (header spelling must match):
`product_name,category,sale_date,quantity,unit_price,region`

Example:
```csv
product_name,category,sale_date,quantity,unit_price,region
Notebook,Stationery,2026-01-12,10,45.50,South
```
Dates must be `YYYY-MM-DD`. Quantity must be a positive whole number. Unit price must be numeric and non-negative. Blank fields and malformed rows are reported.

## Tests
```powershell
python -m pytest -q
```

## Notes
- Upload limit is 8 MB.
- The Sales Records page displays the latest 500 records.
- For a classroom/demo deployment, debug mode is off by default. Keep `SECRET_KEY` private and do not expose the Flask development server publicly.
