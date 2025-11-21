import os
import smtplib
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()

    required_fields = ["to", "subject", "body"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos: to, subject, body"}), 400

    try:
        # Crear email
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USER
        msg["To"] = data["to"]
        msg["Subject"] = data["subject"]

        body = MIMEText(data["body"], "html" if data.get("is_html", False) else "plain")
        msg.attach(body)

        # Enviar correo por SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, data["to"], msg.as_string())

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
