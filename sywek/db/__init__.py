from flask_sqlalchemy import SQLAlchemy
from flask import g, current_app
from datetime import datetime
from sqlalchemy.dialects.postgresql import BIGINT, VARCHAR, JSON, ARRAY

_db = SQLAlchemy()


def init_app(app):
    _db.init_app(app)


def init_db(app):
    with app.app_context():
        _db = get_db()
        _db.create_all()


def get_db():
    if 'db' not in g:
        g.db = _db

    return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()


# article_likes_table = _db.Table('article_likes_table', _db.Column('user_id', _db.Integer, _db.ForeignKey('user_info_table.id')), _db.Column(
#     'article_id', _db.Integer, _db.ForeignKey('user_info_table.id')), _db.Column('likeDT', _db.DateTime, nullable=False))

# article_comments_table = _db.Table(
#     'article_comments_table',
#     _db.Column('user_id', _db.Integer,
#                _db.ForeignKey('user_info_table.id')),
#     _db.Column('article_id', _db.Integer,
#                _db.ForeignKey('user_info_table.id')),
#     _db.Column('replyTo', BIGINT, nullable=False),
#     _db.Column('content', JSON, nullable=False),
#     _db.Column('commentDT', _db.DateTime,
#                nullable=False, default=datetime.utcnow)
# )


class user_info_table(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    name = _db.Column(_db.String(64), nullable=False)
    account = _db.Column(_db.String(128), unique=True, nullable=False)
    passwordHash = _db.Column(_db.String(128), nullable=False)  # sha512
    salt = _db.Column(_db.String(32), nullable=False)
    socialInfo = _db.Column(JSON(), nullable=False)
    verifyAccount = _db.Column(_db.Boolean, default = False)
    followersCount = _db.Column(BIGINT , default = 0)
    userImage = _db.Column(JSON(), nullable=True)
    createDT = _db.Column(_db.DateTime,nullable=False, default=datetime.utcnow)

    # relation
    rs_posts_dy = _db.relationship(
        'articles_table', backref=_db.backref('rs_author', lazy=True), lazy='dynamic')
    rs_likes_dy = _db.relationship('post_likes_table', lazy='dynamic')
    rs_comments_dy = _db.relationship('post_comments_table', lazy='dynamic')
    rs_follows_dy = _db.relationship('follows_table', lazy='dynamic')
    # rs_likes_dy = _db.relationship(
    #     'oAuth_table', secondary=article_likes_table, backref=_db.backref('rs_likes_dy', lazy='dynamic'), lazy='dynamic')
    # rs_ocmmnets_dy = _db.relationship(
    #     'oAuth_table', secondary=article_comments_table, backref=_db.backref('rs_comments_dy', lazy='dynamic'), lazy='dynamic')


class oauth_table(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    user_id = _db.Column(_db.Integer, _db.ForeignKey(
        'user_info_table.id'), nullable=False)
    google = _db.Column(_db.String(256), unique=True, nullable=True)
    github = _db.Column(_db.String(256), unique=True, nullable=True)

    # relation
    rs_user = _db.relationship('user_info_table', uselist=False, lazy=True)


class articles_table(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    author_id = _db.Column(_db.Integer, _db.ForeignKey(
        'user_info_table.id'), nullable=False)
    header = _db.Column(_db.Text, nullable=False)  # null = string.empty
    secondHeader = _db.Column(_db.Text, nullable=False)  # null = string.empty
    headerImage = _db.Column(JSON, nullable=False)
    postDT = _db.Column(_db.DateTime,
                        nullable=False, default=datetime.utcnow)
    tags = _db.Column(ARRAY(VARCHAR), nullable=True)
    content = _db.Column(JSON(), nullable=False)  # null = ''
    likesCount = _db.Column(BIGINT, default=0)
    commentsCount = _db.Column(BIGINT, default=0)
    lastEditDT = _db.Column(_db.DateTime, nullable=False,
                            default=datetime.utcnow)
    # relation
    rs_likes_dy = _db.relationship('post_likes_table', lazy='dynamic')
    rs_comment_dy = _db.relationship('post_comments_table', lazy='dynamic')


class post_likes_table(_db.Model):
    id = _db.Column(BIGINT(), primary_key=True, nullable=False)
    post_id = _db.Column(_db.Integer, _db.ForeignKey(
        'articles_table.id'), nullable=False)
    user_id = _db.Column(_db.Integer, _db.ForeignKey(
        'user_info_table.id'), nullable=False)
    likesDT = _db.Column(
        _db.DateTime, nullable=False, default=datetime.utcnow)


class post_comments_table(_db.Model):
    id = _db.Column(BIGINT(), primary_key=True, nullable=False)
    post_id = _db.Column(_db.Integer, _db.ForeignKey(
        'articles_table.id'), nullable=False)
    user_id = _db.Column(_db.Integer, _db.ForeignKey(
        'user_info_table.id'), nullable=False)
    replyTo = _db.Column(BIGINT)
    content = _db.Column(JSON(), nullable=False)
    commentDT = _db.Column(
        _db.DateTime, nullable=False, default=datetime.utcnow)


class follows_table(_db.Model):
    id = _db.Column(BIGINT(), primary_key=True, nullable=False)
    user_id = _db.Column(_db.Integer, _db.ForeignKey(
        'user_info_table.id'), nullable=False)
    followUser_id = _db.Column(_db.Integer, nullable=False)
    followDT = _db.Column(_db.DateTime,
                          nullable=False, default=datetime.utcnow)
