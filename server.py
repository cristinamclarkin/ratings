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

@app.route("/register")
def register_form():
    """Routes user to registration form"""


    return render_template("registration_form.html")

@app.route("/register", methods=['POST']):
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


@app.route("/login" methods=['GET'])
def user_login():

    return render_template("login_form.html")

@app.route("/login" methods=['POST'])
def user_login():
    email=request.form['email']
    password=request.form['password']
    # If the username exists
    if is_user_in_db(email):
        create_user_session(email, password)
    # Else
    else:
        # Flash a message saying incorrect user_id or password

    return redirect('/', 200)

# Utility functions
def is_user_in_db(email):
    if User.query.filter_by(User.email == email).all():
        return True
    return False

def create_user_session(email, password):
    # password check
    user_to_check = User.query.filter_by(User.email==email, User.password==password).one()
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
