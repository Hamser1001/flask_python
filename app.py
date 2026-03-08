# import required Flask modules
from flask import Flask, render_template, request, redirect, url_for

# import database and models from models.py
from models import db, Book, Author, Review

# module for working with file paths
import os


# create Flask application
app = Flask(__name__)

# get the absolute path of the current project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# ---------------------------
# Application Configuration
# ---------------------------

# configure the SQLite database location
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'books.db')}"
)

# disable modification tracking (saves memory and removes warning)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# initialize SQLAlchemy with the Flask app
db.init_app(app)


# ---------------------------
# Create Database Tables
# ---------------------------

# create database tables automatically if they do not exist
with app.app_context():
    db.create_all()


# ---------------------------
# Routes
# ---------------------------


# home page route
@app.route("/")
def index():
    # get all books from the database
    books = Book.query.all()

    # send books to the template to display them
    return render_template("index.html", books=books)


# route to add a new book
@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    # if the user submits the form
    if request.method == "POST":

        # get data from the form
        title = request.form["title"]
        author_name = request.form["author"]

        # check if the author already exists in the database
        author = Author.query.filter_by(name=author_name).first()

        # if author does not exist, create a new one
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        # create a new book linked to the author
        book = Book(title=title, author_id=author.id)

        # add the book to the database session
        db.session.add(book)

        # save changes to the database
        db.session.commit()

        # redirect the user back to the homepage
        return redirect(url_for("index"))

    # if request method is GET, show the form
    return render_template("add_book.html")


# route to edit an exist book
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    book = Book.query.get_or_404(id)

    # if the user submits the form
    if request.method == "POST":
        # get data from the form
        title = request.form["title"]
        author_name = request.form["author"]

        # check if the author already exists in the database
        author = Author.query.filter_by(name=author_name).first()

        # if author does not exist, create a new one
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        # update the author and the title
        book.author_id = author.id
        book.title = title

        # save changes to the database
        db.session.commit()

        # redirect the user back to the edit page
        return redirect(url_for("index"))

    return render_template("edit_book.html", book=book)


# route to delete an exist book
@app.route("/delete/<int:id>")
def book_delete(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()

    # redirect the user back to the edit page
    return redirect(url_for("index"))


@app.route("/books/<int:id>")
def book_detail(id):
    data = Book.query.get_or_404(id)
    return render_template("book_detail.html", book=data)


@app.route("/search", methods=["GET", "POST"])
def search_books():
    if request.method == "POST":
        query = request.form["query"]
        print(f"query: {query}")
        books = Book.query.filter(Book.title.ilike(f"%{query}%")).all()
        authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
        print(len(books), len(authors))
        return render_template("search.html", books=books, authors=authors, query=query)
    return render_template("search.html")


# ---------------------------
# Run the Application
# ---------------------------

if __name__ == "__main__":
    # start the Flask development server
    app.run(debug=True)
