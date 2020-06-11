# Goodbooks app

import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# database engine object from SQLAlchemy that manages connections to the # DATABASE_URL is an environment variable that indicates where the database db = scoped_session(sessionmaker(bind=engine)) # create a 'scoped session' that ensures different users' interactions with # database are kept separate
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "OCzrG88Hujx2LRMl0UyX2w", "isbns": "9781632168146"})
# print(res.json())


@app.route("/")
def index():
    """Show portfolio of stocks"""
    success_message = "good to go"
    return render_template("index.html", success_message=success_message)


@app.route("/error")
def error():
    return render_template("error.html", message={message})


@app.route("/success")
def success():
    return render_template("success.html", message={message})


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username, 403")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password, 403")

        # Query database for username
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Invalid username and/or password, 403")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/change", methods=["GET", "POST"])
# @login_required
def change():
    """Register user"""
    user = []
    userid = session["user_id"]
    print(userid)

    # Query database for username
    user = db.execute("SELECT id, username, hash FROM users").fetchall()

    for row in user:
        if(row['id'] == userid):
            print(row)
            username = row['username']
            old_hash = row['hash']

    print(username)
    print("old hash: ", old_hash)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("old_password"):
            return render_template("error.html", message="must provide password, 403")

        # Ensure password was submitted
        elif not request.form.get("new_password"):
            return render_template("error.html", message="must provide a new password, 403")

        # Ensure Confirm_password was submitted
        elif not request.form.get("confirm_new_password"):
            return render_template("error.html", message="must provide confirmation password, 403")

        elif (request.form.get("confirm_new_password") != request.form.get("new_password")):
            return render_template("error.html", message="Password and confirmation password don't match, 403")

        # check old password hash key
        if not check_password_hash(old_hash, request.form.get("old_password")):
            return render_template("error.html", message="Must provide correct old password, 403")

        password_hash = generate_password_hash(
            request.form.get("new_password"))

        db.execute("UPDATE users SET hash = :password_hash WHERE username = :username",
                   password_hash={password_hash}, username={username})

        return render_template("login.html")

    else:
        return render_template("change.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # Query database for username
    # execute this SQL command and return for flight in flights
    users = db.execute("SELECT username FROM users").fetchall()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username, 403")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password, 403")

        # Ensure Confirm_password was submitted
        elif not request.form.get("confirm_password"):
            return render_template("error.html", message="must provide confirmation password, 403")

        elif (request.form.get("confirm_password") != request.form.get("password")):
            return render_template("error.html", message="Password and confirmation password don't match, 403")

        # Check if username exists in database
        for user in users:
            if (user['username'].lower() == request.form.get("username").lower()):
                return render_template("error.html", message="This Username already exists, 403")

        # generate password hash key
        password_hash = generate_password_hash(request.form.get("password"))
        name = request.form.get("username").lower()

        print("username: {} hash: {}".format(name, password_hash))

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   {"username": name, "hash": password_hash})
        db.commit()
        return render_template("index.html")

    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
# @login_required
def search():
    # User reached route via POST (as by submitting a form via POST)
    # search for ISBN, AUTHOR ou TITLE based on entry
    if request.method == "POST":
        """Search book"""
        search_book = request.form.get("search_book")
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :search_book OR lower(title) LIKE :search_book OR lower(author) LIKE :search_book ORDER BY title ASC ", {"search_book": "%" + search_book.lower() + "%"}).fetchmany(200)
        
        return render_template("books.html", books=books)
        
    else:
        return render_template("search.html")


# def errorhandler(e):
 #   """Handle error"""
   # if not isinstance(e, HTTPException):
     #   e = InternalServerError()
    # return apology(e.name, e.code)


# Listen for errors
# for code in default_exceptions:
 #   app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug=True)
