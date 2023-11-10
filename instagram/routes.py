import os

from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from instagram.models import load_user, User, Posts, Follow, Block
from instagram import app, database
from instagram.forms import FormLogin, FormCreateNewAccount, FormCreateNewPost, FormFollow, FormUnfollow, FormBlock, \
    FormUnblock
from instagram import bcrypt
from instagram import login_manager


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def homepage():
    formLogin = FormLogin()

    users = []
    posts = []

    if current_user.is_authenticated:
        users = User.query.all()
        followingArr = current_user.following.all()
        blockedByArr = Block.query.filter_by(blocked_id=current_user.id).all()

        for following in followingArr:
            hasBlocked = False

            for blocked in blockedByArr:
                if following.following_id == blocked.blocker_id:
                    hasBlocked = True
                    break

            if not hasBlocked:
                posts += Posts.query.filter_by(user_id=following.following_id).all()

        posts += Posts.query.filter_by(user_id=current_user.id).all()

        posts.sort(key=lambda x: x.creation_date, reverse=True)

    if formLogin.validate_on_submit():
        userToLogin = User.query.filter_by(email=formLogin.email.data).first()
        if userToLogin and bcrypt.check_password_hash(userToLogin.password, formLogin.password.data):
            login_user(userToLogin)
            return redirect(url_for('homepage'))

    return render_template("home.html", form=formLogin, user=current_user, users=users, posts=posts)


@app.route('/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    if int(user_id) == int(current_user.id):
        _formNewPost = FormCreateNewPost()

        posts = current_user.posts.all()
        posts.sort(key=lambda x: x.creation_date, reverse=True)

        if _formNewPost.validate_on_submit():
            _post_text = _formNewPost.text.data

            _post_img = _formNewPost.photo.data
            _img_name = secure_filename(_post_img.filename)
            path = os.path.abspath(os.path.dirname(__file__))
            path2 = app.config['UPLOAD_FOLDER']
            _final_path = f'{path}/{path2}/{_img_name}'

            _post_img.save(_final_path)

            newPost = Posts(post_text=_post_text,
                            post_img=_img_name,
                            user_id=int(current_user.id)
                            )

            database.session.add(newPost)
            database.session.commit()

        return render_template("profile.html", user=current_user, current_user=current_user, form=_formNewPost, posts=posts)
    else:
        _formFollow = FormFollow()
        _formUnfollow = FormUnfollow()
        _formBlock = FormBlock()
        _formUnblock = FormUnblock()

        _user = User.query.get(int(user_id))
        posts = Posts.query.filter_by(user_id=int(user_id)).all()

        posts.sort(key=lambda x: x.creation_date, reverse=True)

        is_following = current_user.following.filter_by(following_id=_user.id).first()
        has_blocked = current_user.blocking.filter_by(blocked_id=_user.id).first()
        is_blocked = _user.blocking.filter_by(blocked_id=current_user.id).first()

        return render_template("profile.html", user=_user, current_user=current_user, form=False,
                               formFollow=_formFollow, formUnfollow=_formUnfollow, formBlock=_formBlock,
                               formUnblock=_formUnblock, is_following=bool(is_following), has_blocked=bool(has_blocked),
                               is_blocked=bool(is_blocked), posts=posts)


@app.route('/unfollow/<user_id>', methods=['POST', 'GET'])
@login_required
def unfollow(user_id):
    _user = User.query.get(int(user_id))
    unfollow = Follow.query.filter_by(follower_id=current_user.id, following_id=_user.id).first()

    database.session.delete(unfollow)
    database.session.commit()

    return redirect(url_for('profile', user_id=user_id))


@app.route('/follow/<user_id>', methods=['POST', 'GET'])
@login_required
def follow(user_id):
    hasBlocked = Block.query.filter_by(blocker_id=current_user.id, blocked_id=user_id).first()

    if hasBlocked:
        return redirect(url_for('profile', user_id=user_id))

    _user = User.query.get(int(user_id))
    newFollow = Follow(follower_id=int(current_user.id),
                       following_id=int(user_id)
                       )

    database.session.add(newFollow)
    database.session.commit()
    return redirect(url_for('profile', user_id=user_id))


@app.route('/block/<user_id>', methods=['POST', 'GET'])
@login_required
def block(user_id):
    _user = User.query.get(int(user_id))
    newBlock = Block(blocker_id=int(current_user.id),
                     blocked_id=int(user_id)
                     )

    isFollowing = Follow.query.filter_by(follower_id=current_user.id, following_id=_user.id).first()

    if isFollowing:
        database.session.delete(isFollowing)

    database.session.add(newBlock)
    database.session.commit()

    return redirect(url_for('profile', user_id=user_id))


@app.route('/unblock/<user_id>', methods=['POST', 'GET'])
@login_required
def unblock(user_id):
    _user = User.query.get(int(user_id))
    unblock = Block.query.filter_by(blocker_id=current_user.id, blocked_id=_user.id).first()

    database.session.delete(unblock)
    database.session.commit()

    return redirect(url_for('profile', user_id=user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/signup', methods=['POST', 'GET'])
def create_account():
    formCreateAccount = FormCreateNewAccount()

    if formCreateAccount.validate_on_submit():
        emailAlreadyExists = User.query.filter_by(email=formCreateAccount.email.data).first()

        if emailAlreadyExists:
            return render_template("signup.html", form=formCreateAccount, error="Email já cadastrado")

        usernameAlreadyExists = User.query.filter_by(username=formCreateAccount.username.data).first()

        if usernameAlreadyExists:
            return render_template("signup.html", form=formCreateAccount, error="Nome de usuário já cadastrado")

        password = formCreateAccount.password.data
        password_cr = bcrypt.generate_password_hash(password)

        newUser = User(username=formCreateAccount.username.data,
                       email=formCreateAccount.email.data,
                       password=password_cr)

        database.session.add(newUser)
        database.session.commit()
        login_user(newUser, remember=True)
        return redirect(url_for('homepage'))

    return render_template("signup.html", form=formCreateAccount)
