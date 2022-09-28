
import secrets
import os
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from website import bcrypt, db, mail
from website.model import User, Post
from website.form import RegistrationForm, LoginForm, AccountForm, CreateForm, UpdateForm, RequestTokenForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message

auth = Blueprint("auth", __name__,template_folder="templates")


@auth.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("auth.account"))
    return render_template("home.html")

@auth.route("/signup", methods=["POST", "GET"] )
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("auth.account"))
    form = RegistrationForm()
    if form.validate_on_submit():
        
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf8")
            user = User(username=form.username.data,  email = form.email.data, password=hashed_password )
            if user and bcrypt.check_password_hash(hashed_password, form.confirm_password.data):
                db.session.add(user)
                db.session.commit()
                flash("Your account has been created.", category="success")
                return redirect(url_for("auth.login"))
    return render_template("sign_up.html", form = form )


@auth.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.account"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if  user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash("Login Successful", category="success")
            return redirect(url_for("auth.account"))
        else:
            flash("Login Unsuccesful, Please check email or password!", category="error")
    return render_template("login.html", form = form)


## To save Pictures and to reduce sizes
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(auth.root_path, "static/images", picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@auth.route("/account", methods = ["POST", "GET"])
@login_required
def account():
    image_file = url_for("static", filename="images/" + current_user.image_file)
    form = AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        flash("Your Account has been updated.", category="success")
        
    elif request.method == "GET":
       form.email.data = current_user.email
       form.username.data = current_user.username
      
    return render_template("account.html", form = form, image_file = image_file)

@auth.route("/create-Idea", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreateForm()
    if form.validate_on_submit():
        post = Post(title= form.title.data, content= form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your Idea has been created.", category="success")
        return redirect(url_for("auth.all_post"))
    return render_template("create_idea.html", form = form)

@auth.route("/all-idea", methods=["GET", "POST"])
@login_required
def all_post():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("all_post.html", posts = posts, page=page)

@auth.route("/mypost/<int:post_id>")
@login_required
def mypost(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("my_post.html", post=post)

@auth.route("/mypost/<int:post_id>/update", methods=["POST", "GET"])
@login_required
def update(post_id):
    form = UpdateForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    elif form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your idea has been updated.", category="success")
        return redirect(url_for("auth.mypost", post_id = post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("update_post.html", form = form )


def send_mail(user):
    token = user.generate_token()
    msg = Message("Password Reset", recipients=[user.email], sender="estheratanang@gmail.com")
    msg.body= f''' If you want to reset your password please follow this link:
    {url_for('auth.reset_password', token=token, _external=True)}
    
    '''

    mail.send(msg)


@auth.route("/reset-request", methods=["GET", "POST"])
def request_token():
    form = RequestTokenForm()

    user = User.query.filter_by(email= form.data["email"]).first()
    if form.validate_on_submit() and user is not None:
        send_mail(user)
        flash("The instructions to reset your password has been sent, Please check your mail.", category="success")
        return redirect(url_for('auth.login'))
    return render_template("request_token.html",form=form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    user = User.verify_token(token)
    if user is None:
        flash("The session has been expired, Please try again.", category="error")
        return redirect(url_for("auth.request_token"))
    if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(password= form.password.data).decode('utf8')
            user.password = hashed_password
            db.session.commit()
            return redirect(url_for("auth.login"))
    return render_template("reset_password.html", form=form)
    



@auth.route("/post/<string:username>", methods=["POST", "GET"])
def your_post(username):
    user = User.query.filter_by(username = username).first_or_404()
    page  = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author= user).paginate(page=page, per_page=5)
    return render_template("your_post.html", posts = posts, user=user)
    

@auth.route("/mypost/<int:post_id>/delete", methods=["POST", "GET"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Your idea has taken away from this universe.", category="error")
        return redirect(url_for("auth.all_post", post_id = post.id))
   

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.home"))