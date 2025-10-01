from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from gmail_service import authenticate_gmail, create_message, send_message

app = Flask(__name__)

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()

    required_fields = ["to", "subject", "body"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos: to, subject, body"}), 400

    try:
        creds = authenticate_gmail()
        service = build("gmail", "v1", credentials=creds)

        # Permitir texto plano o HTML
        message = create_message(
            sender="juan.reyes54587@ucaldas.edu.co",
            to=data["to"],
            subject=data["subject"],
            body=data["body"],
            is_html=data.get("is_html", False)
        )

        result = send_message(service, "me", message)
        return jsonify({"status": "success", "message_id": result["id"]}), 200

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
