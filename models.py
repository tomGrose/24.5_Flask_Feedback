
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Model for creating a User"""

    __tablename__ = "users"

    def __repr__(self):
        """ Show info about a user"""
        return f"<Username: {self.username} First Name: {self.first_name}>"

    

    username = db.Column(db.Text,
                   primary_key=True,
                   unique=True)
    password = db.Column(db.Text,
                    nullable=False)
    email = db.Column(db.Text,
                    unique=True,
                    nullable=False)
    first_name = db.Column(db.Text,
                    nullable=False)
    last_name = db.Column(db.Text, 
                    nullable=False)
    is_admin = db.Column(db.Boolean,
                        default=False)

    feedback = db.relationship("Feedback", cascade="all, delete-orphan")

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register a user with a hashed password and then return that user"""
        hashedpw = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashedpw.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Check that the username exists, and match passwords. Return the user"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False
   

class Feedback(db.Model):
    """Model for creating Feedback"""

    __tablename__ = "feedback"

    def __repr__(self):
        """ Show info about the feedback a user left"""
        return f"<Username: {self.username} Title: {self.title}>"

    

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.Text,
                    nullable=False)
    content = db.Column(db.Text,
                    unique=True,
                    nullable=False)
    username = db.Column(db.Text,
                    db.ForeignKey('users.username'))

    user = db.relationship('User')