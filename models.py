from exts import db
from flask_sqlalchemy import SQLAlchemy


# user_user = db.Table(
# 	'user_user',
# 	db.Column('user_id_following', db.Integer, db.ForeignKey('user.id'), primary_key=True),
# 	db.Column('user_id_followed', db.Integer, db.ForeignKey('user.id'), primary_key=True)
# )

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
	# follow = db.relationship('User', secondary=user_user, backref=db.backref('users'))


class Article(db.Model):
	__tablename__ = 'article'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	time = db.Column(db.String(50), nullable=False)
	title = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	author = db.relationship('User', backref=db.backref('articles'))


class Plate(db.Model):
	__tablename__ = 'plate'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String(100), nullable=False)


class Essays(db.Model):
	__tablename__ = 'Essays'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	time = db.Column(db.String(50), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	author = db.relationship('User', backref=db.backref('essays'))


class Message(db.Model):
	__tablename__ = 'message'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	time = db.Column(db.String(50), nullable=False)
	content = db.Column(db.Text, nullable=False)


sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
sender = db.relationship('User', backref=db.backref('messages'))
receive_id = db.Column(db.Integer, db.ForeignKey('user.id'))
receive = db.relationship('User', backref=db.backref('receive_messages'))


class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	time = db.Column(db.String(50), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	author = db.relationship('User', backref=db.backref('comment'))
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
	article = db.relationship('Article', backref=db.backref('comment'))
