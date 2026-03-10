from app import app


# import database and models from models.py
from models import db, Book, Author, Review


# import required Flask modules
from flask import Flask, render_template, request, redirect, url_for


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
        from tasks import send_book_notification

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

        # fire celery to send notification
        send_book_notification.delay(book.id, book.title)

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
