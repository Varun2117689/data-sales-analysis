from models import Sale
from services.csv_service import process_csv

def test_upload_and_duplicate_policy(app):
    csv_data = b"product_name,category,sale_date,quantity,unit_price,region\\nPen,Stationery,2026-01-01,2,10,South\\n"
    with app.app_context():
        first = process_csv(csv_data)
        second = process_csv(csv_data)
        assert first["inserted"] == 1
        assert second["duplicates"] == 1
        assert Sale.query.count() == 1

def test_invalid_row_reported(app):
    csv_data = b"product_name,category,sale_date,quantity,unit_price,region\\nPen,Stationery,wrong-date,2,10,South\\n"
    with app.app_context():
        result = process_csv(csv_data)
        assert result["inserted"] == 0
        assert len(result["errors"]) == 1

def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200
