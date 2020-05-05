# [Project 1: Books](https://docs.cs50.net/web/2020/x/projects/1/project1.html)

Web Programming with Python and JavaScript

**Assignment:**
In this project, you’ll build a book review website. Users will be able to register for your website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. You’ll also use the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via your website’s API.

## Usage

### Requirements

Make sure that you have [Python3, pip](https://docs.python.org/3/installing/index.html) and [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/) installed and configured correctly.

This application comes with a `requirements.txt` file which contains the module names required to run. In order to install them simply run:

```
pip3 install -r requirements.txt
```

Installing separate or missing modules and libraries is done by running:

```
$ pip3 install <module-name>
```

### Setup

In order to seed the database with data from `books.csv` run `import.py`

> Note: For this to work you will have to configure your database and set the environment variable from the next step, otherwise the script will not be able to connect to the database.

The following tables will be created:

- users
- authors
- books
- reviews

After creating the tables the script will fill the database with the books. This could take a while, so time to grab a coffee...

### Running the application

This application makes use of the [Goodreads API](https://www.goodreads.com/api). As soon as you register a developer account with Goodreads, you will get a `key` and `secret` with which you can perform the calls required to fetch the book review data required in this application.

Make a file in your project called `secrets.py` and make two fields:

```
key = "<your-key-here>"
secret = "<your-secret-here>"
```

These values will get imported in `application.py`

Next export `DATABASE_URL` in the terminal, so the application can use this environment variable to connect to the database:

```
$ export DATABASE_URL=<your-database-url>
```

> For debugging and using automatic reloading simply type `export FLASK_DEBUG=1` in the terminal to enable debug mode

To run the application execute these commands:

```
$ export FLASK_APP=application
$ flask run
```

The flask application should now be running on `http://127.0.0.1:5000/`

## Architecture and Design

This application uses [Flask](https://flask.palletsprojects.com/en/1.1.x/), a Python micro-framework that helps with RESTful handling of data, application routing and template binding for rendering the data from:

1. Goodreads API
2. PostgreSQL database hosted on [Heroku](https://www.heroku.com/)
