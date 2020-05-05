"""
Seed database with users, reviews and ratings
"""
import csv
import os
from random import randint

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
DB = scoped_session(sessionmaker(bind=engine))


def main():
    FILE = open("MOCK_DATA (1).csv")
    reader = csv.reader(FILE)

    firstline = True
    for username, password, content, rating in reader:
        # skip first line of csv file
        if firstline:
            firstline = False
            continue

        # fill users table
        DB.execute(
            """--sql
        INSERT INTO users (username, password) VALUES (:username, :password) ON CONFLICT DO NOTHING
        --endsql""", {
                "username": username,
                "password": generate_password_hash(password)
            })

        print("added user")

        # add review for user
        DB.execute(
            """--sql
        INSERT INTO reviews (content, rating, book_id, user_id) VALUES
        (:content, :rating, :book_id, (SELECT user_id FROM users WHERE username=:username LIMIT 1))
        --endsql""",
            {
                "content": content,
                "rating": rating,
                # add book_id for book you want to add the reviews for
                "book_id": randint(200, 400),
                "username": username
            })

        print("added review")
        DB.commit()


if __name__ == "__main__":
    main()
