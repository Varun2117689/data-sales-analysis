import io
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from dotenv import load_dotenv
from models import db, Product, Sale
from services.csv_service import process_csv
from services.analytics import build_dashboard_data, create_monthly_chart

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-this-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///sales.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def dashboard():
        data = build_dashboard_data()
        chart = create_monthly_chart(data["monthly"])
        return render_template("dashboard.html", data=data, chart=chart)

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "POST":
            file = request.files.get("file")
            if not file or not file.filename:
                flash("Please choose a CSV file.", "error")
                return redirect(url_for("upload"))
            if not file.filename.lower().endswith(".csv"):
                flash("Only .csv files are supported.", "error")
                return redirect(url_for("upload"))
            content = file.read()
            try:
                result = process_csv(content)
            except UnicodeDecodeError:
                flash("The CSV must be UTF-8 encoded.", "error")
                return redirect(url_for("upload"))
            flash(
                f"Import complete: {result['inserted']} added, "
                f"{result['duplicates']} duplicates skipped, "
                f"{len(result['errors'])} invalid rows.",
                "success" if result["inserted"] or not result["errors"] else "error"
            )
            if result["errors"]:
                app.config["LAST_ERROR_REPORT"] = result["errors"]
                return render_template("upload.html", result=result)
            return render_template("upload.html", result=result)
        return render_template("upload.html", result=None)

    @app.route("/reports/errors.csv")
    def download_errors():
        errors = app.config.get("LAST_ERROR_REPORT", [])
        output = io.StringIO()
        output.write("row_number,reason,raw_data\n")
        import csv
        writer = csv.writer(output)
        for item in errors:
            writer.writerow([item["row_number"], item["reason"], item["raw_data"]])
        mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
        return send_file(mem, mimetype="text/csv", as_attachment=True,
                         download_name="csv_validation_errors.csv")

    @app.route("/sales")
    def sales():
        rows = Sale.query.order_by(Sale.sale_date.desc(), Sale.id.desc()).limit(500).all()
        return render_template("sales.html", rows=rows)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(413)
    def too_large(_error):
        flash("File is too large. Maximum upload size is 8 MB.", "error")
        return redirect(url_for("upload"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
