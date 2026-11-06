from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column("product_id", db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=False, default="Uncategorized")
    sales = db.relationship("Sale", back_populates="product")

class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column("sale_id", db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(100), nullable=False, default="Unknown")
    sale_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship("Product", back_populates="sales")

    @property
    def revenue(self):
        return self.quantity * self.unit_price
