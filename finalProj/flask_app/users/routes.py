from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm, SearchForm
from ..models import User

users = Blueprint("users", __name__)

""" ************ User Management views ************ """


# TODO: implement

@users.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("spotify.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)




@users.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('users.index'))

    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')

            user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
            user.save()
            return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


# TODO: implement
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.objects(username=form.username.data).first()

            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('users.account'))
            else:
                flash("Please Authenticate Again")
    return render_template('login.html', form=form)


# TODO: implement
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.index'))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()
    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            # TODO: handle update username form submit
            try:
                update_username_form.validate_username(update_username_form.username.data)
                
            except:
                print("stuff")
                

            newUsername = update_username_form.username.data

            current_user.username = newUsername

            current_user.save()
            
            return redirect(url_for('users.login'))

        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate():
            # TODO: handle update profile pic form submit
            image = update_profile_pic_form.picture.data
            filename = secure_filename(image.filename)
            content_type = f'images/{filename[-3:]}'

            if current_user.profile_pic.get() is None:
                # user doesn't have a profile picture => add one
                current_user.profile_pic.put(
                    image.stream, content_type=content_type)
            else:
                # user has a profile picture => replace it
                current_user.profile_pic.replace(
                    image.stream, content_type=content_type)
            current_user.save()

            return redirect(url_for('users.account'))

    profile_pic_bytes = BytesIO(current_user.profile_pic.read())
    profile_pic_base64 = base64.b64encode(
        profile_pic_bytes.getvalue()).decode()
    # TODO: handle get requests
    return render_template('account.html', update_username_form=update_username_form, update_profile_pic_form=update_profile_pic_form, image=profile_pic_base64)
