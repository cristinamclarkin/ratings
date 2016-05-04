"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Show user details."""

    # create instance of user based on user_id from url
    display_user = User.query.get(user_id)

    return render_template('user.html', display_user=display_user)


@app.route("/register")
def register_form():
    """Routes user to registration form"""


    return render_template("registration_form.html")

@app.route("/register", methods=['GET', 'POST'])
def handle_form_data():

    password = request.form['password']
    age = request.form['age']
    email= request.form['email']
    zipcode = request.form['zipcode']

    # Check if the user_id is taken
    if not is_user_in_db(user_id):
        # Create a user
        new_user = User(password=password, age=age, email=email, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()

    create_user_session(email, password, )
    return redirect('/', 200)


@app.route("/login")
def user_login():

    return render_template("login_form.html")

@app.route("/login", methods=['POST'])
def user_login():
    email=request.form['email']
    password=request.form['password']
    # If the username exists
    if is_user_in_db(email):
        create_user_session(email, password)
        return redirect ('/', 200)
    else:
        return redirect('/register', 200)


@app.route("/logout")
def log_out_user():
    """Logging out user and redirecting to homepage."""

    #ends session
    del session["user_id"]
    
    flash("You are now logged out.")
    
    return redirect("/", 200)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    #sorts movies by title and returns a list of all titles in db.
    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:movie_id>")
def show_movie_details(movie_id):
    """Show movie details."""

    movie = Movie.query.get(movie_id)

    return render_template("movie_details.html",
                            movie=movie)
@app.route("/movies/<int:movie_id>/show-rating-form")
def show_rating_form(movie_id):
    """Show rating form to add or update movie rating."""

    # If user is logged in, render rating_form.html.
    # Otherwise, redirect to login page.
    
    movie = Movie.query.get(movie_id)    

    if session:
        return render_template("rating_form.html",
                                movie=movie)
    else:
        flash("Please login to add or update a movie rating.")
        return redirect("/login")

@app.route('/movies/<int:movie_id>/user-rating', methods=['POST'])
def display_form(movie_id):

    # extract form info
    score = request.form.get('score')

    # rating = db.session.query(Rating).filter(Rating.user_id == session['user'], Rating.movie_id == movie_id).first()
    rating = Rating.query.filter(Rating.user_id == session['user_id'], Rating.movie_id == movie_id).first()
    
    # if user has already submitted a score for this movie, then update DB
    if rating:
        rating.score = score
    # else, add new rating to DB
    else:
        rating = Rating(user_id=session['user_id'], movie_id=movie_id, score=score)
        db.session.add(rating)
        
    db.session.commit()

    flash(("Your rating of {} has been saved!").format(score))

    return redirect("/movies/<int:movie_id>", movie_id=movie_id)


# Utility functions
def is_user_in_db(email):
    if User.query.filter_by(User.email == email).all():
        return True
    return False

def create_user_session(email, password):
    # password check
    user_to_check = User.query.filter_by(User.email==email, User.password==password).one()
    if not password == user_to_check.password:
        flash("Incorrect password")
        return redirect("/login")
    # Create flask session
    session["user_id"] = user_to_check.user_id
    # flash message saying user logged in
    flash('You were successfully logged in')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
