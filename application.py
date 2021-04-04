from flask import Flask, render_template, request, session, redirect, flash
from flask_caching import Cache
import sqlite3
import datetime
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


app = Flask(__name__)
db = sqlite3.connect('database.db', check_same_thread=False)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@login_required
def index():
    hist = db.execute("SELECT * FROM track WHERE user_id = ?", (session["user_id"],))
    return render_template("index.html", hist=hist)


@app.route('/login', methods=["GET", "POST"])
def login():
    name = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Please provide username")
            return render_template("login.html")
        elif not request.form.get("password"):
            flash("Please provide password")
            return render_template("login.html")
        else:
            rows = db.execute("SELECT * FROM users WHERE username = ?", (name,))
            row_count = 0
            for row in rows:
                paswd = row
                row_count += 1
            if row_count != 1 or not check_password_hash(paswd[2], password):
                return redirect("/error")
            session["user_id"] = paswd[0]
            flash("Logged in.")
            return redirect("/")
    else:
        return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide username")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide password")
            return render_template("register.html")

        # Ensure both password matches
        elif not request.form.get("confirmation"):
            flash("Please confirm password")
            return render_template("register.html")

        # Check if password match
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password does not match")
            return render_template("register.html")

        else:
            name = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")
            pwdhash = generate_password_hash(password)
            results = db.execute("SELECT username FROM users WHERE username = ?", (name,))
            count = 0
            for row in results:
                count += 1

            if count == 0:
                # Insert user details to database
                db.execute("INSERT INTO users (username, hash, email) VALUES(?, ?, ?)", (name, pwdhash, email))
                rows = db.execute("SELECT * FROM users WHERE username = ?", (name,))
                db.commit()
                uid = 0
                for row in rows:
                    uid = row[0]
                session["user_id"] = uid
                # Redirect user to home page
                flash("Registered!")
                return redirect("/")
            else:
                return redirect("/error")
    else:
        return render_template("register.html")


@app.route("/error")
def error():
    return render_template("error.html")


@app.route("/c_password", methods=["GET", "POST"])
@login_required
def c_password():
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            flash("Please type in your new password")
            return render_template("c_password.html")
        elif not confirmation:
            flash("Please confirm your password")
            return render_template("c_password.html")
        elif password != confirmation:
            flash("Password does not match!")
            return render_template("c_password.html")
        else:
            hash_password = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", (hash_password, session["user_id"]))
            flash("Password changed!")
            return redirect("/")
    else:
        return render_template("c_password.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    flash("Logout successful!")
    return redirect("/")


@app.route("/amazon", methods=["GET", "POST"])
@login_required
def amazon():
    if request.method == "POST":
        url = request.form.get("url")
        price = request.form.get("price")
        p_name = request.form.get("product")
        ntime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        price = float(price)
        if not url:
            return redirect("/error")
        if not price:
            return redirect("/error")
        else:
            db.execute("INSERT INTO track(user_id, product_url, price, product_name, track_time) VALUES(?,?,?,?,?)", (session["user_id"], url, price, p_name, ntime))
            db.commit()
            flash("Product is being tracked!")
            return redirect("/")
    else:
        return render_template("amazon.html")

@app.route("/delete", methods=["POST"])
def delete():
    tr_date = request.form.get("sl")
    new_tr = str(tr_date)
    flash("Deleted!")
    db.execute("DELETE FROM track WHERE track_time = ?", (new_tr,))
    db.commit()
    return redirect("/")
