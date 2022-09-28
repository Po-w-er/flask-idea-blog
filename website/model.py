from difflib import restore
from email.policy import default
from website import app
from website import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
import jwt

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable= False, default="default.jpg")
    password = db.Column(db.String, unique=True, nullable=False)
    # User can have many posts
    posts = db.relationship("Post", backref="author", lazy=True)
    def __repr__(self):
        f"User('{self.username}', '{self.email}', '{self.password}')"

    #generating token with jwt
    def generate_token(self):
        reset_token = jwt.encode({"user_id":self.id, "exp": datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
        return reset_token

    @staticmethod
    def verify_token(token):
        try:
            user_id = jwt.decode(token,app.config["SECRET_KEY"], algorithms="HS256")["user_id"]
        except:
            None
        return User.query.get(user_id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # In other to create a on e to many relationship, we need to create a foreign key that links the primary key to the Post table, Which is user.id(This refers the name of the column, so we need to use a lower case.)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        f"Post'{self.title}','{self.date_posted}'"