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
def show_user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """Show user details."""

    # create instance of user based on user_id from url
    display_user = User.query.get(user_id)

    return render_template('user.html', user=display_user)


@app.route("/register")
def show_registery():
    """Routes user to registration form"""

    return render_template("registration_form.html")


@app.route("/process_register", methods=['POST'])
def process_registry():
    password = request.form.get('password')
    age = int(request.form.get('age'))
    email= request.form.get('email')
    zipcode = request.form.get('zipcode')

    user = User.query.filter_by(email=email).first()
    # Check if the user_id is taken
    if user:
        return redirect('/login', 200)

    else:
        # Create a user
        new_user = User(password=password, age=age, email=email, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()

    create_user_session(email, password)
    return redirect('/', 200)


@app.route("/login")
def show_user_login():

    return render_template("login.html")

@app.route("/process_login", methods=['POST'])
def process_user_login():
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
def show_movie_list():
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


    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    rating_scores = [r.score for r in movie.ratings]
    average = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    # Either use the prediction or their real rating

    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif user_rating:
        # User has already scored for real; use that
        effective_rating = user_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating

    the_eye = User.query.filter_by(email="the-eye@of-judgment.com").one()
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

    # Depending on how different we are from the Eye, choose a message

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has brought me" +
            " to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly failed you.",
        "That movie is great. For a clown to watch. Idiot.",
        "Words cannot express the awfulness of your taste."
    ]

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]
        print "Beratement is {}".format(beratement)
    else:
        beratement = None

  
    # {% if beratement %}
    #   <p>Balloonicorn's mom says "{{ beratement }}".</p>
    # {% endif %}


    # return render_template(
    #     "ratings.html",
    #     movie=movie,
    #     user_rating=user_rating,
    #     average=average,
    #     prediction=prediction,
    #     beratement = beratement
    #     )

    return render_template(
        "ratings.html",
        movie=movie,
        user_rating=user_rating,
        average=average,
        prediction=prediction
        )


#    return render_template("ratings.html",
#                                movie=movie, average=average, prediction=prediction)


@app.route('/movies/<int:movie_id>/user-rating', methods=['POST'])
def process_ratings_form(movie_id):

    # extract form info
    score = request.form.get('score')

    rating = Rating.query.filter(Rating.user_id == session['user_id'], Rating.movie_id == movie_id).first()

    #movie = Movie.query.filter(Movie.movie_id == movie_id).first()

    # if user has already submitted a score for this movie, then update DB
    if rating:
        #old_score = rating.score
        rating.score = score

        #print "In process_ratings_form - Updating score for {} from {} to {}".format(movie.title, old_score, rating.score)
    # else, add new rating to DB
    else:
        rating = Rating(user_id=session['user_id'], movie_id=movie_id, score=score)
        db.session.add(rating)

        #print "in process_ratings_form - Adding score for {} as {}".format(movie.title, rating.score)
        
    db.session.commit()

    flash(("Your rating of {} has been saved!").format(score))

    return redirect("/movies/" + str(movie_id), 200)

@app.route("/ratings")
def show_ratings():
    movie = Movie.query.get(5)  
    #print movie 

    return render_template("ratings.html",
                                movie=movie)



# Utility functions
def is_user_in_db(email):
    print "is_user_in_db - Checking user with email {}".format(email)
    user = User.query.filter_by(email=email).first()
    if user:
        return True
    return False

def create_user_session(email, password):
    # password check
    user_to_check = User.query.filter_by(email=email, password=password).first()
    if not user_to_check:
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
