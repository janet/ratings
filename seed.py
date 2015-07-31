"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
from datetime import datetime



def load_users():
    """Load users from u.user into database."""
    seed_user_file = open("seed_data/u.user")
    for line in seed_user_file:
        line = line.rstrip()
        seed_user_line = line.split("|")
        
        new_user = User(
            user_id=int(seed_user_line[0]),
            age=int(seed_user_line[1]),
            zipcode=seed_user_line[4]
            )
        db.session.add(new_user)
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    seed_movie_file = open("seed_data/u.item")
    for line in seed_movie_file:
        line = line.rstrip()
        seed_movie_line = line.split("|")
        released_at_string = seed_movie_line[2]

        if released_at_string == '':
            released_at_date = None 
        else:
            released_at_date = datetime.strptime(released_at_string, "%d-%b-%Y")

        if seed_movie_line[1] == 'unknown':
            movie_title = seed_movie_line[1]
        else:
            movie_title = seed_movie_line[1][0:-7]
            movie_title = movie_title.decode("latin-1")

        new_movie = Movie(
            movie_id=int(seed_movie_line[0]),
            title=movie_title,
            released_at=released_at_date,
            imdb_url=seed_movie_line[4]
            )
        
        db.session.add(new_movie)
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""
    seed_rating_file = open("seed_data/u.data")

    row_count = 0

    for line in seed_rating_file:
        row_count += 1

        line = line.rstrip()
        seed_rating_line = line.split("\t")
        
        new_rating = Rating(
            user_id=int(seed_rating_line[0]),
            movie_id=int(seed_rating_line[1]),
            score=int(seed_rating_line[2]),
            )
        db.session.add(new_rating)

        if row_count == 1000:
            db.session.commit()
            row_count = 0

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # load_users()
    load_movies()
    # load_ratings()
