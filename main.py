import os
import smtplib
from datetime import date
from functools import wraps

import bleach
import yagmail
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from forms import CommentForm, ContactForm, CreatePostForm, LoginForm, RegisterForm

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def only_admins(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return decorated_function


app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager.init_app(app)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="blog")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(100))
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    blog_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    blog = relationship("BlogPost", back_populates="comments")


gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None,
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    db.create_all()


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data

        already_exists = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if already_exists:
            flash("User already exists")
            return redirect("/login")

        password = generate_password_hash(form.password.data, "scrypt", 8)
        name = form.name.data

        new_user = User(email=email, password=password, name=name)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html", form=form, user=current_user)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if not user:
            flash("A user with this email does not exist.")
            return redirect(url_for("login"))

        correct_password = check_password_hash(user.password, password)

        if correct_password:
            login_user(user)
            print("Logged in")
            return redirect("/")
        else:
            flash("Incorrect credentials, try again.")

    return render_template("login.html", form=form, user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


@app.route("/")
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You are not authenticated.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment.data,
            author=current_user,
            blog=requested_post,
        )

        db.session.add(new_comment)
        db.session.commit()

    return render_template(
        "post.html", post=requested_post, form=form, user=current_user
    )


@app.route("/new-post", methods=["GET", "POST"])
@only_admins
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@only_admins
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template(
        "make-post.html", form=edit_form, is_edit=True, user=current_user
    )


@app.route("/delete/<int:post_id>")
@only_admins
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html", user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        try:
            yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
            yag.send(
                to="muricamar2004@gmail.com",
                subject=f"Message from {name}",
                contents=f"{message}\nSend them an email @ {email}",
            )
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

        return redirect(url_for("get_all_posts"))

    return render_template("contact.html", form=form, user=current_user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
