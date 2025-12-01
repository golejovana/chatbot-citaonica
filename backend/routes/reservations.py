from flask import Blueprint, request, jsonify, session
from db import cursor, db
from routes.auth import login_required

reservations_bp = Blueprint("reservations_bp", __name__)

@reservations_bp.route("/reserve", methods=["POST"])
@login_required
def reserve():
    user_id = session["user_id"]
    data = request.get_json()
    date = data.get("date")

    cursor.execute(
        "INSERT INTO reservations (user_id, date) VALUES (%s, %s)",
        (user_id, date)
    )
    db.commit()

    return jsonify({"success": True, "message": "Rezervacija kreirana!"})


@reservations_bp.route("/my-reservations")
@login_required
def my_reservations():
    user_id = session["user_id"]
    cursor.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
    result = cursor.fetchall()
    return jsonify(result)
