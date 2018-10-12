from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bird(db.Model):
    """Bird Information"""

    __tablename__ = "birds"

    bird_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    common_name = db.Column(db.String(50), nullable=False)
    scientific_name = db.Column(db.String(50), nullable=False)
    habitat = db.Column(db.String(50), nullable=True)
    number = db.Column(db.Integer, nullable=True)
    # picture_id = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return 'Bird ID: {}, Common Name: {}, Scientific Name: {}'.format(self.bird_id, self.common_name, self.scientific_name)


class User(db.Model):
    """User Information"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return 'User ID: {}, First Name: {}, Last Name: {}'.format(self.user_id, self.fname, self.lname)


class Favorite(db.Model):
    """User's saved favorites. If a record exists here, it is a favorite."""

    __tablename__ = "favorites"

    favorite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bird_id = db.Column(db.Integer, 
                        db.ForeignKey('birds.bird_id')) #table.attribute
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.user_id'))
    fav_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User',
                           backref=db.backref("favorites",
                                              order_by=favorite_id))
    bird = db.relationship('Bird')
    # if backref existed here, we would have relationship to # of times 
    #a bird has been favorited between all users 
    
    def __repr__(self):
        """Provide helpful representation when printed."""

        return 'User ID: {}, Bird ID: {}'.format(self.user_id, self.bird_id)


class Checklist(db.Model):
    """Checklist of birds user has bookmarked - can be seen or unseen"""

    __tablename__ = "checklist"

    checklist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bird_id = db.Column(db.Integer, 
                        db.ForeignKey('birds.bird_id'))
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.user_id'))
    seen = db.Column(db.Boolean, default=False)
    seen_date = db.Column(db.DateTime, nullable=False)
    add_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User',
                            backref=db.backref("checklist",
                                          order_by=checklist_id))
    bird = db.relationship('Bird')


    def __repr__(self):
        """Provide helpful representation when printed."""

        return 'User ID: {}, Bird ID: {}, Seen: {}'.format(self.user_id, self.bird_id, self.seen)

# class Following(db.Model):
#     """Table of users and other users they have added to follow"""
#     __tablename__ = "following"

#     followee_id = db.Column(db.Integer,
#                   db.ForeignKey(users.user_id))
#     following_id = db.Column(db.Integer,
#                    db.ForeignKey())


# def __repr__(self):
#         """Provide helpful representation when printed."""

#     return f"""<Following followee_id={self.followee_id} 
#                follower_id={self.follower_id} 
#                """

# Helper Functions

def connect_to_db(app):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///birdwatch'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app 
    connect_to_db(app)
    print("Connected to DB.")
