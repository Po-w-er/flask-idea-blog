from ast import Pass
from flask_wtf import FlaskForm
from website.model import User
from wtforms import StringField, EmailField, PasswordField, SubmitField,  BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username =  StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=12), EqualTo("confirm_password", message="Passwords do not match!" )])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords do not match!")])
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = User.query.filter_by(username= username.data).first()
        if user:
            raise ValidationError("That username already exists, Please choose another.")
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("Email already exists!")
    


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class AccountForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

    def validate_email(self, email):
        if email.data != current_user.email:
           user = User.query.filter_by(email = email.data).first()
           if user:
              raise ValidationError("Email is already in use")
              
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data ).first()
            if user: 
                raise ValidationError("Username has been taken")
        
class CreateForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired(), Length(max=500, min=1)])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create")


class UpdateForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired(), Length(max=500, min=1)])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Update")



class RequestTokenForm(FlaskForm):
    email = EmailField("Email",  validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Email does not exist, Please register and try again.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(max=12, min=8)])
    confirm_password = PasswordField('confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')
