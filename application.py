import json
import os
from secrets import key, secret

import requests
import xmltodict
from flask import (Flask, g, jsonify, redirect, render_template, request,
                   session, url_for)
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
TEMPLATES_AUTO_RELOAD = True

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
DB = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def search():
    query = ""
    errors = []
    # check if there is a logged in user
    try:
        ID = session["user_id"]
        pass
    except KeyError:
        return redirect("/login")

    if request.method == "POST":
        # get and validate form data
        if not request.form.get("search"):
            errors.append("Please enter a search term")
            pass
        else:
            # use input to do API call to goodreads
            query = request.form.get("search")
            response = requests.get("https://www.goodreads.com/search.xml",
                                    params={
                                        "key": key,
                                        "q": query,
                                        "search": "all"
                                    })

            works = (xmltodict.parse(response.content, process_namespaces=True)
                     ["GoodreadsResponse"]["search"]["results"]["work"])

            return render_template("search.html", errors=errors, works=works)

    return render_template("search.html", errors=errors)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    errors = []
    if request.method == "POST":
        # get and validate form data
        if not request.form.get("username"):
            errors.append("Please provide a username")
            pass

        elif not request.form.get("password"):
            errors.append("Please provide a password")
            pass

        # proceed if no errors
        elif not errors:
            username = request.form.get("username")
            password = request.form.get("password")
            user = DB.execute(
                """--sql
            SELECT * FROM users WHERE username=:username
            --endsql""", {
                    "username": username
                }).fetchone()

            # check if user exists
            if user is None:
                errors.append("User not found")
                pass

            # check if password is correct
            elif not check_password_hash(user.password, password):
                errors.append("Incorrect password")
                pass

            # proceed if STILL no errors
            elif not errors:
                # Remember which user has logged in
                session["user_id"] = user.id
                return redirect("/")

    return render_template("login.html", errors=errors)


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        # get and validate form data

        # check if username is provided
        if not request.form.get("username"):
            errors.append("Please provide a username")
            pass

        # check if password is provided
        elif not request.form.get("password"):
            errors.append("Please provide a password")
            pass

        # check if username and password match
        elif request.form.get("password") != request.form.get(
                "password-confirmation"):
            errors.append("Passwords don't match")
            pass

        # proceed if no errors
        elif not errors:
            username = request.form.get("username")
            password = generate_password_hash(request.form.get("password"))

            DB.execute(
                """--sql
            INSERT INTO users (username, password) VALUES (:username, :password)
            --endsql""", {
                    "username": username,
                    "password": password
                })

            DB.commit()
            return redirect("/login")

    return render_template("register.html", errors=errors)
