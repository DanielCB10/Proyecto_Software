import os
from io import BytesIO
from flask import Flask, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "proyecto_seguridad")
DB_TYPE = os.getenv("DB_TYPE", "mysql+pymysql")  # usar mysql+pymysql para MySQL/MariaDB

DATABASE_URI = f"{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))


    def as_dict(self):
        return {
            "id": self.id,
            "nombre": self.name,
            "email": self.email,
        }

@app.route("/health")
def health():
    try:
        # prueba de conexión 
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

def fetch_usuarios():
    """
    Devuelve lista de diccionarios con los usuarios.
    Si la tabla usuarios tiene otras columnas, puedes usar una consulta raw:
    db.session.execute(text("SELECT * FROM usuarios")).fetchall()
    """
    usuarios = Usuario.query.all()
    return [u.as_dict() for u in usuarios]

@app.route("/report/excel")
def report_excel():
    try:
        rows = fetch_usuarios()
        if not rows:
            df = pd.DataFrame(columns=["id", "nombre", "email", "telefono", "creado_en"])
        else:
            df = pd.DataFrame(rows)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="usuarios")
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="usuarios_report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/report/pdf")
def report_pdf():
    try:
        rows = fetch_usuarios()

        # Si no hay datos
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph("Reporte de Usuarios", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))

        if not rows:
            elements.append(Paragraph("No se encontraron usuarios.", styles["Normal"]))
            doc.build(elements)
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="usuarios_report.pdf", mimetype="application/pdf")

        headers = list(rows[0].keys())
        data = [headers]
        for r in rows:
            data.append([str(r.get(h, "")) if r.get(h, "") is not None else "" for h in headers])

        table = Table(data, repeatRows=1)
        # Estilo
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 10),
            ("BOTTOMPADDING", (0,0), (-1,0), 8),
            ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name="usuarios_report.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
