"""Member Management System: a Flask app where people register for
membership, an administrator approves or rejects applications, and approved
members can log in, manage their own details and appear in a public list.

Data is stored in a MySQL database ("member_management") in a "users" table.
Columns used by this file: id, name, national_id, phone, address, birth_date,
sex, email, password_hash, avatar, status ("pending" / "approved" /
"rejected") and role ("admin" for administrators).

Routes:
    GET        /                      Home page with links to the main pages.
    GET/POST   /login                 Log in (approved members only).
    GET/POST   /register              Submit a membership application.
    GET        /registration-success  Confirmation shown after registering.
    GET        /members               Public list of approved members.
    GET        /profile/<member_id>   Public profile of one approved member.
    GET        /dashboard             Logged-in member's own page.
    POST       /edit-info             Update own name, email, phone, address.
    POST       /change-password       Change own password.
    GET        /logout                Log out.
    GET        /admin                 Admin only: list pending applications.
    POST       /approve-application   Admin only: approve an application.
    POST       /reject-application    Admin only: reject an application.

Login state is kept in Flask's session as session["user_id"].
"""

from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)

# Secret key used to sign the session cookie (login state and flash
# messages).
app.secret_key = "Flask_Seccret_Key"

# Reject any request body larger than 2 MB (this also limits avatar uploads).
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Folder where uploaded profile photos are saved (static/images).
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")

# A single database connection shared by every route in this file.
# Each route creates its own cursor from it.
db = mysql.connector.connect(
    host="localhost",
    user="member_app",
    password="MySQLConnection_NewUser_Password",
    database="member_management"
)


@app.route("/")
def home():
    """Show the home page (links to login, registration and members)."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Show the login form (GET) or check the submitted credentials (POST).

    On a successful login the user's id is stored in the session and they
    are sent to the dashboard. Users whose application has not been approved
    yet cannot log in. The same message is returned for an unknown email and
    a wrong password, so it doesn't reveal which emails are registered.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        # Commit ends the read transaction so later queries on this shared
        # connection see up-to-date data.
        db.commit()

        # Passwords are stored as hashes, never as plain text
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
    """Show the registration form (GET) or save a new application (POST).

    Validates the name, email and password, checks that the optional avatar
    is an image type, and inserts the user (status is left to the database
    default, which is expected to be "pending"). If an avatar was uploaded
    it is saved to static/images and its file name stored on the user row.
    Duplicate emails or national IDs are caught as an IntegrityError.
    """
    if request.method == "POST":
        # Read every field from the submitted form
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


        # --- Validation ---
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

        # Only accept common image file extensions for the profile photo
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

            # The photo is saved after the insert because its file name
            # includes the new user's id.
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
            # Raised when email or national_id violates a UNIQUE constraint
            db.rollback()
            return "Email or national ID already registered!"


    return render_template("register.html")

@app.route("/members")
def members():
    """Show the public list of approved members (name and photo only)."""
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
    """Show the public profile of one approved member.

    Args:
        member_id (int): The user's id (taken from the URL).

    Pending or rejected users are treated as not found, so their profiles
    can't be viewed. Only id, name, avatar and email are exposed.
    """
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
    """Show the logged-in member's own page with their full details.

    Redirects to the login page if nobody is logged in, or if the user in
    the session no longer exists in the database.
    """
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
        # Stale session (e.g. the user was deleted): log them out
        session.clear()
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


@app.route("/edit-info", methods=["POST"])
def edit_info():
    """Update the logged-in user's name, email, phone and address.

    Requires a login. Name and email are validated; if the new email is
    already used by someone else the update is rolled back.
    """
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
        # The new email belongs to another account
        db.rollback()
        return "That email is already registered!"

    return redirect(url_for("dashboard"))

@app.route("/change-password", methods=["POST"])
def change_password():
    """Change the logged-in user's password.

    The current password must be correct and the new one must be typed
    twice identically and be at least 8 characters long. Results are shown
    on the dashboard using flash messages (category "error" or "success").
    """
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
    """Log the user out by clearing the session."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    """Admin page listing every application that is still pending.

    Requires a login and role "admin"; anyone else is redirected to the
    login page or shown "Access denied!".
    """
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
    """Admin only: mark a pending application as approved.

    The applicant's id comes from the "applicant_id" form field. The UPDATE
    only affects users whose status is still "pending", so already-handled
    applications are left alone.
    """
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    # Check that the logged-in user is an administrator
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

    # Must be present and made only of digits
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
    """Admin only: mark a pending application as rejected.

    Works exactly like approve_application(), but sets the status to
    "rejected" instead.
    """
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    # Check that the logged-in user is an administrator
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
    """Confirmation page shown after a successful registration."""
    return render_template("registration_success.html")


