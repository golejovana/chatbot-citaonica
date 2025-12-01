from flask import Blueprint, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from db import cursor, db
from functools import wraps

auth_bp = Blueprint("auth_bp", __name__)

# -------------------------------
# LOGIN REQUIRED DEKORATOR
# -------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# -------------------------------
# LOGIN PAGE
# -------------------------------
@auth_bp.route("/login")
def login_page():
    return render_template("login.html")

# LOGIN API
@auth_bp.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Nepostojeći korisnik ili pogrešna lozinka!"})

    # SPAŠAVAMO U SESSION
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return jsonify({"success": True, "message": "Uspješno ste ulogovani!"})


# -------------------------------
# REGISTER PAGE
# -------------------------------
@auth_bp.route("/register")
def register_page():
    return render_template("register.html")

# REGISTER API
@auth_bp.route("/api/register", methods=["POST"])
def register_api():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = generate_password_hash(data.get("password"))

    # provjera postoji li email
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"success": False, "message": "Email već postoji!"})

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    db.commit()

    return jsonify({"success": True, "message": "Registracija uspješna!"})

# -------------------------------
# LOGOUT
# -------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

