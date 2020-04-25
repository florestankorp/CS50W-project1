import json
import os
from secrets import key, secret

import requests
from flask import Flask, g, redirect, render_template, request, session
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


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        if not request.form.get("username"):
            errors.append("Please provide a username")
            pass

        elif not request.form.get("password"):
            errors.append("Please provide a password")
            pass

        elif request.form.get("password") != request.form.get(
                "password-confirmation"):
            errors.append("Passwords don't match")
            pass

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
            return redirect("/")

    return render_template("register.html", errors=errors)


# {
#     'books': [{
#         'id': 29207858,
#         'isbn': '1632168146',
#         'isbn13': '9781632168146',
#         'ratings_count': 1,
#         'reviews_count': 6,
#         'text_reviews_count': 0,
#         'work_ratings_count': 28,
#         'work_reviews_count': 129,
#         'work_text_reviews_count': 9,
#         'average_rating': '  4.14'
#     }]
# }
