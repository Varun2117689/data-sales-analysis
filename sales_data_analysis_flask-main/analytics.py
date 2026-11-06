import base64
from io import BytesIO
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from models import Sale

def sales_frame():
    rows = Sale.query.all()
    records = [{
        "product": row.product.product_name,
        "category": row.product.category,
        "sale_date": row.sale_date,
        "quantity": row.quantity,
        "unit_price": row.unit_price,
        "region": row.region,
        "revenue": row.quantity * row.unit_price
    } for row in rows]
    return pd.DataFrame(records)

def build_dashboard_data():
    df = sales_frame()
    if df.empty:
        return {"revenue": 0, "quantity": 0, "count": 0, "products": [], "monthly": []}
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    product_summary = (df.groupby("product", as_index=False)
        .agg(quantity=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values(["revenue", "quantity"], ascending=False))
    monthly_summary = (df.assign(month=df["sale_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False).agg(revenue=("revenue", "sum"), quantity=("quantity", "sum"))
        .sort_values("month"))
    return {
        "revenue": float(df["revenue"].sum()),
        "quantity": int(df["quantity"].sum()),
        "count": int(len(df)),
        "products": product_summary.to_dict("records"),
        "monthly": monthly_summary.to_dict("records")
    }

def create_monthly_chart(monthly):
    if not monthly:
        return None
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot([x["month"] for x in monthly], [x["revenue"] for x in monthly], marker="o")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
