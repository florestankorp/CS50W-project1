import json
import os
from secrets import key, secret

import requests

from flask import (Flask, Response, g, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
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
        elif not errors:
            # use input to do API call to goodreads
            query = request.form.get("search")
            formatted_query = f'%{query.lower()}%'
            books = DB.execute(
                """--sql
            SELECT book_id, isbn, title, year, name as author FROM books 
            JOIN authors ON books.author_id = authors.author_id 
            WHERE 
            LOWER(isbn) LIKE :query OR
            LOWER(title) LIKE :query OR
            LOWER(name) LIKE :query
            --endsql""", {
                    "query": formatted_query
                }).fetchall()

            return render_template("search.html", errors=errors, books=books)

        else:
            errors.append("Book not found")
            pass

    return render_template("search.html", errors=errors)


@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    errors = []

    # check if user is logged in
    try:
        ID = session["user_id"]
        pass
    except KeyError:
        return redirect("/login")

    # get book from database based on isbn and return JSON response
    book = DB.execute(
        """--sql
            SELECT title, name AS author,year, isbn, 
                COUNT(review_id) AS review_count,
                ROUND(AVG(rating)::numeric,2) AS average_score 
            FROM books
            JOIN authors USING(author_id)
            JOIN reviews USING(book_id)
            WHERE isbn=:isbn
            GROUP BY authors.name, book_id
            --endsql""", {
            "isbn": isbn
        }).fetchone()

    if book is None:
        return app.response_class(response="Book not found",
                                  status=404,
                                  mimetype='application/json')

    return jsonify(dict(book))


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    errors = []
    # check if user is logged in
    try:
        ID = session["user_id"]
        pass
    except KeyError:
        return redirect("/login")

    if not book_id:
        return redirect("/")

    book = DB.execute(
        """--sql
            SELECT book_id, isbn, title, year, name AS author FROM books
            JOIN authors USING(author_id)
            WHERE book_id=:book_id
            --endsql""", {
            "book_id": book_id
        }).fetchone()

    reviews = DB.execute(
        """--sql
            SELECT * FROM reviews
            JOIN users USING(user_id)
            WHERE book_id=:book_id
            --endsql""", {
            "book_id": book_id
        }).fetchall()

    if book is None:
        return redirect("/")

    if request.method == "POST":

        # get and validate form data
        if not request.form.get("review"):
            errors.append("Please provide review")
            pass

        if not request.form.get("rating"):
            errors.append("Please provide rating")
            pass

        # proceed if no errors
        elif not errors:
            content = request.form.get("review")
            rating = request.form.get("rating")

            # save rating
            DB.execute(
                """--sql
            INSERT INTO reviews (user_id, book_id, content, rating) VALUES (:user_id, :book_id, :content, :rating)
            --endsql""", {
                    "user_id": ID,
                    "book_id": book_id,
                    "content": content,
                    "rating": rating
                })

            DB.commit()
            return redirect(url_for('book', book_id=book_id))
    # check if user has already reviewed book, if so he can't review again
    has_user_placed_review = []
    for review in reviews:
        has_user_placed_review.append(review.user_id == ID)

    can_user_place_review = True not in has_user_placed_review

    # api call
    goodreads_reviews = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={
            "key": key,
            "isbns": book.isbn
        }).json()

    return render_template("book.html",
                           errors=errors,
                           book=book,
                           reviews=reviews,
                           goodreads_reviews=goodreads_reviews,
                           can_user_place_review=can_user_place_review)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")


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
                session["user_id"] = user.user_id
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

            user = DB.execute(
                """--sql
            SELECT * FROM users WHERE username=:username
            --endsql""", {
                    "username": username,
                }).fetchone()

            # check if user exists
            if user is None:
                DB.execute(
                    """--sql
                INSERT INTO users (username, password) VALUES (:username, :password)
                --endsql""", {
                        "username": username,
                        "password": password
                    })

                DB.commit()
                return redirect("/login")
            else:
                errors.append("User already exists")
                pass

    return render_template("register.html", errors=errors)
