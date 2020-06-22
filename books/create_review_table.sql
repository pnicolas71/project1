CREATE TABLE reviews (
    bookid VARCHAR NOTNULL,
    user_id INTEGER NOT NULL,
    review_id SERIAL PRIMARY KEY,
	review_text VARCHAR NOT NULL,
	review_rating SMALLINT NOT NULL,
	review_date  DATE NOT NULL 
);