"""

In a Python file called import.py separate from your web application, write a program that will take the books and import them into your PostgreSQL database. You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another. Run this program by running python3 import.py to import the books into your database, and submit this program with the rest of your project code.

"""
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
DB = scoped_session(sessionmaker(bind=engine))


def main():
    DB.execute("""--sql
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(255)
    )--endsql""")

    # name has to be unique so there are no conflicts when inserting author_id into books table
    DB.execute("""--sql
    CREATE TABLE IF NOT EXISTS authors (
        author_id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    )--endsql""")

    DB.execute("""--sql
    CREATE TABLE IF NOT EXISTS books (
        book_id SERIAL PRIMARY KEY,
        isbn VARCHAR(255),
        title VARCHAR(255),
        year VARCHAR(255),
        author_id INTEGER REFERENCES authors
    )--endsql""")

    DB.execute("""--sql
    CREATE TABLE IF NOT EXISTS reviews (
        review_id SERIAL PRIMARY KEY,
        content TEXT,
        rating INTEGER,
        user_id INTEGER REFERENCES users,
        book_id INTEGER REFERENCES books
    )--endsql""")

    print("created tables")

    FILE = open("books.csv")
    reader = csv.reader(FILE)

    firstline = True
    for isbn, title, author, year in reader:
        # skip first line of csv file
        if firstline:
            firstline = False
            continue

        # fill authors table with authors first, so we can use those id's as references when filling the books table
        DB.execute(
            """--sql
        INSERT INTO authors (name) VALUES (:name) ON CONFLICT DO NOTHING
        --endsql""", {"name": author})

        print("inserted author")

        DB.execute(
            """--sql
        INSERT INTO books (isbn, title, year, author_id) VALUES (:isbn, :title, :year, (
                SELECT author_id FROM authors WHERE name=:author
            )
        ) 
        --endsql""", {
                "isbn": isbn,
                "title": title,
                "year": year,
                "author": author,
            })

        print("inserted book")
    DB.commit()


if __name__ == "__main__":
    main()
