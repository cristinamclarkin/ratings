"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import correlation


# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user.
        Takes self and second user"""

        user_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            # Create our keys of movie_ids for movies we've seen
            user_ratings[rating.movie_id] = rating

        for other_rating in other.ratings:
            # Get the rating for a movie we've rated that's in the other 
            # user's movie ratings
            user_rating = user_ratings.get(other_rating.movie_id)
            # If there's actually a rating
            if user_rating:
                # Add it to the list of pairs
                paired_ratings.append( (user_rating.score, other_rating.score) )

        # If we have any pairs to get similarity with, get the correlation
        if paired_ratings:
            return correlation.pearson(paired_ratings)
        # Else, return no correlation
        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict user's rating of a movie.
        Takes a movie object """

        other_ratings = movie.ratings

        similarities = [ (self.similarity(other_rating.user), other_rating) for other_rating in other_ratings]

        similarities.sort(reverse=True)

        similarities = [(sim, other_rating) for sim, other_rating in similarities if sim > 0]

        if not similarities:
            return None

        numerator = sum([other_rating.score * sim for sim, other_rating in similarities])
        denominator = sum([sim for sim, other_rating in similarities])

        return numerator/denominator


    def __repr__(self):
        return "<User user_id={} email={} password={} age={} zipcode={}>".format(
            self.user_id, self.email, self.password, self.age, self.zipcode)



class Movie(db.Model):
    """Movie in ratings website"""
    
    __tablename__ = "movies"


    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    release_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return "<Movie movie_id={} title={} release_at={} imdb_url={}>".format(
            self.movie_id, self.title, datetime.strftime(self.release_at, "%Y-%m-%d"), self.imdb_url)

class Rating(db.Model):
    """Ratings of various movies on websiteM"""

    __tablename__ = "ratings"
    
    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=True)

    # Define relationship to user
    #user = db.relationship("User",
    #                       backref=db.backref("ratings", order_by=rating_id))
    
    # Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to user
    user = db.relationship("User",
                            backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        return "<Rating rating_id={} movie_id={} user_id={} score={}>".format(
            self.rating_id, self.movie_id, self.user_id, self.score)



# Put your Movie and Rating model classes here.


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
