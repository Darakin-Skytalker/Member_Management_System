from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "Flask_Seccret_Key"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")

db = mysql.connector.connect(
    host="localhost",
    user="member_app",
    password="MySQLConnection_NewUser_Password",
    database="member_management"
)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        db.commit()
        if user and check_password_hash(user["password_hash"], password):
            if user["status"] != "approved":
                return "Your application is still awaiting approval!"

            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        national_id = request.form.get("national_id")
        phone = request.form.get("Phone_NO")
        address = request.form.get("address")
        birth_date = request.form.get("Birth_Date")
        sex = request.form.get("sex")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        avatar = request.files.get("avatar")


        if not name or not name.strip():
            return "Name is required!"
        name = name.strip()

        if not email or "@" not in email:
            return "A valid email is required!"

        if not password or password != confirm_password:
            return "Passwords do not match!"
        if len(password) < 8:
            return "Password must be at least 8 characters long!"
        password_hash = generate_password_hash(password)

        extension = None
        if avatar:
            allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp"}
            extension = avatar.filename.rsplit(".", 1)[-1].lower()
            if extension not in allowed_extensions:
                return "Invalid file type!"

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users
                (name, national_id, phone, address, birth_date, sex, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (name, national_id, phone, address, birth_date, sex, email, password_hash)
            )
            db.commit()

            member_id = cursor.lastrowid
            if extension:
                avatar_filename = f"{name}_img_{member_id}.{extension}"
                avatar_path = os.path.join(UPLOAD_FOLDER, avatar_filename)
                avatar.save(avatar_path)

                cursor.execute(
                    "UPDATE users SET avatar = %s WHERE id = %s",
                    (avatar_filename, member_id)
                )
                db.commit()

            return redirect(url_for("registration_success"))

        except mysql.connector.IntegrityError:
            db.rollback()
            return "Email or national ID already registered!"


    return render_template("register.html")

@app.route("/members")
def members():
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, avatar
        FROM users
        WHERE status = %s
        """,
        ("approved",)
    )
    members = cursor.fetchall()

    return render_template("members.html", members=members)

@app.route("/profile/<int:member_id>")
def profile(member_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, avatar, email
        FROM users
        WHERE id = %s AND status = %s
        """,
        (member_id, "approved")
    )
    member = cursor.fetchone()

    if member is None:
        return "Member not found!", 404

    return render_template("profile.html", member=member)


@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


@app.route("/edit-info", methods=["POST"])
def edit_info():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")

    if not name or not name.strip():
        return "Name is required!"

    if not email or "@" not in email:
        return "A valid email is required!"

    name = name.strip()

    cursor = db.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET name = %s, email = %s, phone = %s, address = %s
            WHERE id = %s
            """,
            (name, email, phone, address, user_id)
        )
        db.commit()
    except mysql.connector.IntegrityError:
        db.rollback()
        return "That email is already registered!"

    return redirect(url_for("dashboard"))

@app.route("/change-password", methods=["POST"])
def change_password():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")
    if not current_password or not new_password or not confirm_new_password:
        return "All password fields are required!"

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT password_hash FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    db.commit()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if not check_password_hash(user["password_hash"], current_password):
        flash("Current password is incorrect!", "error")
        return redirect(url_for("dashboard"))

    if new_password != confirm_new_password:
        flash("New passwords do not match!", "error")
        return redirect(url_for("dashboard"))

    if len(new_password) < 8:
        flash("Password must be at least 8 characters long!", "error")
        return redirect(url_for("dashboard"))

    new_password_hash = generate_password_hash(new_password)

    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (new_password_hash, user_id)
    )
    db.commit()

    flash("Password changed successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT role FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    db.commit()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if user["role"] != "admin":
        return "Access denied!"

    cursor.execute(
        """SELECT id, name, email, phone, address, national_id,
        birth_date, avatar FROM users 
        WHERE status = %s""",
        ("pending",)
    )
    pending_users = cursor.fetchall()

    return render_template("admin.html", pending_users=pending_users)

@app.route("/approve-application", methods=["POST"])
def approve_application():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT role FROM users WHERE id = %s",
        (user_id,)
    )

    user = cursor.fetchone()
    db.commit()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if user["role"] != "admin":
        return "Access denied!"

    applicant_id = request.form.get("applicant_id")

    if not applicant_id or not applicant_id.isdigit():
        flash("Invalid applicant ID!", "error")
        return redirect(url_for("admin"))

    cursor.execute(
        """
        UPDATE users
        SET status = 'approved'
        WHERE id = %s AND status = 'pending'
        """,
        (applicant_id,)
    )
    db.commit()

    return redirect(url_for("admin"))


@app.route("/reject-application", methods=["POST"])
def reject_application():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT role FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    db.commit()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if user["role"] != "admin":
        return "Access denied!"

    applicant_id = request.form.get("applicant_id")

    if not applicant_id or not applicant_id.isdigit():
        flash("Invalid applicant ID!", "error")
        return redirect(url_for("admin"))

    cursor.execute(
        """
        UPDATE users
        SET status = 'rejected'
        WHERE id = %s AND status = 'pending'
        """,
        (applicant_id,)
    )
    db.commit()

    return redirect(url_for("admin"))


@app.route("/registration-success")
def registration_success():
    return render_template("registration_success.html")


