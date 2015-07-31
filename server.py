"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

from sqlalchemy.orm.exc import NoResultFound


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    session["user_id"] = None
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """Show user detail including list of movies they have rated."""

    user_object = User.query.filter_by(user_id=user_id).one()
    

    # user_ratings = Rating.query.filter_by(user_id=user_id).all()
    user_ratings = db.session.query(Movie.title, Rating.score).join(Rating).filter(Rating.user_id == user_id).all()
    
    
    return render_template("user_detail.html", 
        user_id=user_object.user_id,
        user_email=user_object.email,
        user_age=user_object.age, 
        user_zipcode=user_object.zipcode, 
        user_ratings=user_ratings)

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    """Show movie detail including list of ratings."""

    movie = Movie.query.filter_by(movie_id=movie_id).one()

    return render_template("movie_detail.html", 
        movie=movie)

@app.route('/login')
def login():
    """Login form for user entry of their data"""

    return render_template("login.html")

@app.route('/process_login', methods=['POST'])
def process_login():
    """Process login form: Authenticate user and if new user, add to database"""

    email_entered = request.form.get("email")
    password_entered = request.form.get("password")
    
    try:
        user_queried = User.query.filter_by(email=email_entered).one()
        if user_queried.password != password_entered:
            flash("Password is incorrect. Please re-enter.")
            return redirect('/login') #re-enter password
        else:
            loggedin_user_id = user_queried.user_id

    except NoResultFound:
        new_user = User(
            email=email_entered,
            password=password_entered
        )

        db.session.add(new_user)
        db.session.commit()
        # db.session.flush()
        loggedin_user_id = new_user.user_id

    #adding logged in user to session
    session['user_id'] = loggedin_user_id 

    #created new user or validated existing user password and redirecting to home
    flash("Logged in")

    return redirect('/users/' + str(loggedin_user_id)) 

@app.route('/logout')
def logout():
    """Logout route that redirects to the homepage"""
    flash("Logged out")

    print "before: ", session['user_id']

    session['user_id'] = None

    print "after: ", session['user_id']

    return redirect('/')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()