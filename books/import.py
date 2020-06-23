# Goodbooks app

import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Set up database
# database engine object from SQLAlchemy that manages connections to the # DATABASE_URL is an environment variable that indicates where the database db = scoped_session(sessionmaker(bind=engine)) # create a 'scoped session' that ensures different users' interactions with # database are kept separate
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
# loop gives each column a name
for isbn, title, author, year in reader:
    if isbn != "isbn":
        db.execute("INSERT INTO books (isbn, title, author, pb_year) VALUES (:isbn, :title, :author, :pb_year)",
                   {"isbn": isbn, "title": title, "author": author, "pb_year": year})  # substitute values from CSV line into books
        print(isbn, title, author, year)
db.commit()  # transactions are assumed, so close the transaction finished