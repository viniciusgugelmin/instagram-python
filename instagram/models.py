from instagram import database, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Follow(database.Model):
    follower_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False, primary_key=True)
    following_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False, primary_key=True)



class Block(database.Model):
    blocker_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False, primary_key=True)
    blocked_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False, primary_key=True)


class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False, unique=True)
    email = database.Column(database.String, nullable=False, unique=True)
    password = database.Column(database.String, nullable=False)

    posts = database.relationship("Posts", backref='user', lazy='dynamic')

    following = database.relationship('Follow', foreign_keys=[Follow.follower_id],
                                      backref=database.backref('follower', lazy='joined'),
                                      lazy='dynamic', cascade='all, delete-orphan')

    blocking = database.relationship('Block', foreign_keys=[Block.blocker_id],
                                     backref=database.backref('blocker', lazy='joined'),
                                     lazy='dynamic', cascade='all, delete-orphan')


class Posts(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    post_text = database.Column(database.String, default='')
    post_img = database.Column(database.String, default='default.png')
    creation_date = database.Column(database.String, nullable=False, default=datetime.utcnow())
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)