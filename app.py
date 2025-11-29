from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# API – prima poruku sa frontenda
@app.route("/api/message", methods=["POST"])
def api_message():
    data = request.get_json()
    user_message = data.get("message", "")

    # za sada samo echo – da znamo da radi
    reply = f"Primila sam poruku: {user_message}"

    return jsonify({"answer": reply})


if __name__ == "__main__":
    app.run(debug=True)
