from exts import db
from flask_sqlalchemy import *

# user_user = db.Table(
# 	'user_user',
# 	db.Column('user_id_following', db.Integer, db.ForeignKey('user.id'), primary_key=True),
# 	db.Column('user_id_followed', db.Integer, db.ForeignKey('user.id'), primary_key=True)
# )


article_user = db.Table('article_user',
                        db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                        )

essay_user = db.Table('essay_user',
                      db.Column('essay_id', db.Integer, db.ForeignKey('Essays.id'), primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                      )

secret_user = db.Table('secret_user',
                       db.Column('secret_id', db.Integer, db.ForeignKey('secret.id'), primary_key=True),
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                       )


class Follow(db.Model):
    __tablename__ = 'follow'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    self_introduction = db.Column(db.Text, nullable=True)


# follow = db.relationship('User', secondary=user_user, backref=db.backref('users'))


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('articles'))
    like = db.relationship('User', secondary=article_user, backref=db.backref('like_articles'))


# class Plate(db.Model):
#     __tablename__ = 'plate'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(100), nullable=False)


class Essays(db.Model):
    __tablename__ = 'Essays'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('essays'))
    like = db.relationship('User', secondary=essay_user, backref=db.backref('like_essays'))


class Secret(db.Model):
    __tablename__ = 'secret'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('secrets'))
    like = db.relationship('User', secondary=secret_user, backref=db.backref('like_secrets'))


# class Message(db.Model):
#     __tablename__ = 'message'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     time = db.Column(db.String(50), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#
#
# sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
# sender = db.relationship('User', backref=db.backref('messages'))
# receive_id = db.Column(db.Integer, db.ForeignKey('user.id'))
# receive = db.relationship('User', backref=db.backref('receive_messages'))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('comment'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    article = db.relationship('Article', backref=db.backref('comment'))


# class like(db.Model):
#     __tablename__ = 'like'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     # 	db.Column('user_id_following', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#     # 	db.Column('user_id_followed', db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     liked_user_id = db.Column(db.Integer, db.ForeignKey('article.id'))
#     like_article_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class SecretComment(db.Model):
    __tablename__ = 'secretcomment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('secret_comment'))
    article_id = db.Column(db.Integer, db.ForeignKey('secret.id'))
    article = db.relationship('Secret', backref=db.backref('comment'))
