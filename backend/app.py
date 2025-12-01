from flask import Flask
from routes.chatbot import chatbot_bp
from routes.auth import auth_bp
from routes.reservations import reservations_bp
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super_secret_key" # omogucava flask-u da vidi ko je ulogovan

# registracija ruta
app.register_blueprint(chatbot_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(reservations_bp)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4002, debug=True)
