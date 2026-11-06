import csv
import hashlib
import io
from datetime import datetime
from models import db, Product, Sale

REQUIRED_COLUMNS = ["product_name", "category", "sale_date", "quantity", "unit_price", "region"]

def _clean(value):
    return (value or "").strip()

def process_csv(file_bytes):
    """Import valid rows. Duplicate policy: identical normalized sale rows are skipped."""
    text = file_bytes.decode("utf-8-sig")
    stream = io.StringIO(text)
    reader = csv.DictReader(stream)
    if not reader.fieldnames:
        raise ValueError("CSV is empty or has no header.")
    headers = [h.strip() for h in reader.fieldnames]
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    inserted = duplicates = 0
    errors = []
    for row_number, raw in enumerate(reader, start=2):
        raw_data = str(raw)
        try:
            # DictReader stores extra fields under key None for malformed rows.
            if None in raw or any(v is None for k, v in raw.items() if k is not None):
                raise ValueError("Malformed row: number of values does not match header.")
            values = {key: _clean(raw.get(key)) for key in REQUIRED_COLUMNS}
            if not all(values.values()):
                raise ValueError("One or more required values are blank.")
            try:
                sale_date = datetime.strptime(values["sale_date"], "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("sale_date must use YYYY-MM-DD format.")
            try:
                quantity = int(values["quantity"])
                unit_price = float(values["unit_price"])
            except ValueError:
                raise ValueError("quantity must be an integer and unit_price must be numeric.")
            if quantity <= 0:
                raise ValueError("quantity must be greater than zero.")
            if unit_price < 0:
                raise ValueError("unit_price cannot be negative.")

            normalized = "|".join([
                values["product_name"].casefold(), values["category"].casefold(),
                sale_date.isoformat(), str(quantity), f"{unit_price:.4f}",
                values["region"].casefold()
            ])
            digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            if Sale.query.filter_by(sale_hash=digest).first():
                duplicates += 1
                continue

            product = Product.query.filter_by(product_name=values["product_name"]).first()
            if product is None:
                product = Product(product_name=values["product_name"], category=values["category"])
                db.session.add(product)
                db.session.flush()
            else:
                product.category = values["category"]

            db.session.add(Sale(
                product_id=product.id, sale_date=sale_date, quantity=quantity,
                unit_price=unit_price, region=values["region"], sale_hash=digest
            ))
            db.session.flush()
            inserted += 1
        except ValueError as exc:
            errors.append({"row_number": row_number, "reason": str(exc), "raw_data": raw_data})
    db.session.commit()
    return {"inserted": inserted, "duplicates": duplicates, "errors": errors}
