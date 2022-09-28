from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__) 
app.config["SECRET_KEY"] = "AKRGUIRREJSGARGUYR97EGJDG49450"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"


# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'estheratanang@gmail.com'
app.config['MAIL_PASSWORD'] = 'oohbgmbizsygxaxr'
app.config['MAIL_USE_TLS'] = True


#You should update configuration before initializing the mail or wrappig it around the app
mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page. "
login_manager.login_message_category = "error"
from .auth import auth
from website.handler import error

app.register_blueprint(auth, url_prefix = "/")
app.register_blueprint(error, url_prefix="/")