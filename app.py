import os
from flask import Flask, request, jsonify
# Nuevas importaciones de SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# --- Variables de Entorno ---
# Necesitamos EMAIL_USER (remitente) y la nueva clave de SendGrid
EMAIL_USER = os.environ.get("EMAIL_USER") # Usado como remitente
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY") # Usado para autenticar la API
# EMAIL_PASS ya NO es necesario

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()

    required_fields = ["to", "subject", "body"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos: to, subject, body"}), 400

    # Verificación de clave antes de intentar enviar
    if not SENDGRID_API_KEY or not EMAIL_USER:
        return jsonify({"status": "error", "message": "Faltan variables de entorno (SENDGRID_API_KEY o EMAIL_USER)."}), 500

    try:
        # 1. Construir el mensaje usando la librería de SendGrid
        message = Mail(
            from_email=EMAIL_USER,
            to_emails=data["to"],
            subject=data["subject"],
            # Asumimos que data["body"] es HTML si data.get("is_html", False) es True
            html_content=data["body"] if data.get("is_html", False) else None,
            plain_text_content=data["body"] if not data.get("is_html", False) else None
        )

        # 2. Conectarse y enviar a través de la API (HTTPS)
        # Esto elimina el uso inestable de smtplib y el puerto 587
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        # El envío ocurre aquí
        response = sg.send(message)

        # 3. Verificar el estado de la respuesta de la API (200 o 202 indican éxito)
        if response.status_code in [200, 202]:
            return jsonify({"status": "success", "message": "Correo enviado vía SendGrid."}), 200
        else:
            # Si SendGrid devuelve un error, lo registramos.
            print(f"Error en SendGrid: Código {response.status_code}, Cuerpo: {response.body.decode()}")
            return jsonify({"status": "error", "message": f"Fallo en API de SendGrid: {response.status_code}"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Nota: Render usa el puerto 10000. 5000 es típico para desarrollo local.
    app.run(port=5000)