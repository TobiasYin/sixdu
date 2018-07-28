from flask import Flask, url_for, render_template, redirect, session, g, request
from models import *
import config
from check_code import get_check_code
import os
import time
from mistune import markdown
from clean_html import clean_html

app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)

with app.app_context():
	db.create_all()

path_list = []


def md2html(md):
	# print(markdown(md))
	return markdown(md)


def get_time():
	times = time.strftime("%H:%M:%S")
	days = time.strftime("%Y-%m-%d")
	return days + ' ' + times


@app.before_request
def get_request():
	username = session.get('username')
	if username:
		temp_user = User.query.filter(User.username == username).first()
		if user:
			g.user = temp_user
		else:
			redirect(url_for('login'))


@app.context_processor
def send_user():
	if hasattr(g, 'user'):
		return {'user': g.user}
	else:
		return {'user': None}


@app.route('/')
def index():
	result1 = Article.query.all()
	length = len(result1)
	if length != 0:
		article_last = result1[-1]
		if length != 1:
			result1 = result1[::-1][1:min(length, 4)]
		else:
			result1 = []
	else:
		article_last = None
	result2 = Essays.query.all()
	if result2:
		result2 = result2[-5:][::-1]
	kw = {'cream': result1, 'essays': result2, 'len': len, 'articlelast': article_last, 'clean': clean_html}
	return render_template('index.html', **kw)


@app.route('/article/<article_id>')
def article(article_id):
	result = Article.query.filter(Article.id == article_id).first()
	return render_template('article.html', article=result, len=len)


@app.route('/comment/<comment_id>', methods=['GET', 'POST'])
def comment(comment_id):
	if request.method == 'GET':
		return render_template('publishfail.html', failcode='不能访问此页面')
	else:
		if hasattr(g, 'user'):
			new_content = request.form.get('comment')
			if new_content:
				time_now = get_time()
				new_comment = Comment(content=new_content, author_id=g.user.id, time=time_now, article_id=comment_id)
				db.session.add(new_comment)
				db.session.commit()
				return redirect(url_for('article', article_id=comment_id))
			else:
				return render_template('publishfail.html', failcode='评论内容不能为空')
		else:
			return render_template('publishfail.html', failcode='没有权限')


@app.route('/articles')
def articles():
	article_result = Article.query.all()
	if article_result:
		article_result = article_result[::-1]
	kw = {'cream': article_result, 'len': len, 'clean': clean_html}
	return render_template('articles.html', **kw)


@app.route('/tags')
def tags():
	result = Plate.query.all()
	kw = {'plate': result, 'length': len(result)}
	return render_template('tags.html', **kw)


@app.route('/message')
def message():
	result = Message.query.all()
	result = result[::-1]
	kw = {'messages': result, 'length': len(result)}
	return render_template('message.html', **kw)


@app.route('/essays')
def essays():
	result = Essays.query.all()
	result = result[::-1]
	kw = {'essays': result, 'len': len}
	return render_template('essays.html', **kw)


@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	global path_list
	for path in path_list:
		try:
			# os.remove('/var/www/web/static/image/code/code' + path + '.jpg')
			os.remove('static/image/code/code' + path + '.jpg')
		except FileNotFoundError as e:
			print(e, '\n\n')
			print('Path Error')
		finally:
			print('Occur Error')
	path_list = []
	if request.method == 'GET':
		return render_template('login.html')
	else:
		username = request.form.get('username')
		temp_user = User.query.filter(User.username == username).first()
		if temp_user:
			if temp_user.password == request.form.get('password'):
				session['username'] = temp_user.username
				if request.form.get('remember') == 'on':
					session.permanent = True
				return redirect(url_for('index'))
			else:
				return render_template('loginfail.html', failcode='密码错误')
		else:
			return render_template('loginfail.html', failcode='没有找到用户')


@app.route('/exits')
def exits():
	session.clear()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	global path_list
	if request.method == 'GET':
		check_code, md5, path = get_check_code()
		path_list.append(path)
		session['check_code'] = check_code
		return render_template('register.html', path=path, check_code=md5)
	else:
		check_code = session.get('check_code')
		username = request.form.get('username')
		password = request.form.get('password')
		password_repeat = request.form.get('password_re')
		if username and password and password_repeat:
			if check_code == request.form.get('check_code').lower():
				if password_repeat != password:
					return render_template('registerfail.html', failcode='两次输入密码不相同')
				temp_user = User.query.filter(User.username == username).first()
				if temp_user:
					return render_template('registerfail.html', failcode='用户名已存在')
				else:
					temp_user = User(username=username, password=password)
					db.session.add(temp_user)
					db.session.commit()
					return redirect(url_for('login'))
			else:
				return render_template('registerfail.html', failcode='验证码错误')
		else:
			return render_template('registerfail.html', failcode='密码或用户名不能为空')


@app.route('/user/<user_id>')
def user(user_id):
	result = User.query.filter(User.id == user_id).first()
	if hasattr(g, 'user'):
		follow_result = Follow.query.filter(Follow.following_id == g.user.id, Follow.followed_id == user_id).first()
		if follow_result:
			is_followed = True
		else:
			is_followed = False
	else:
		is_followed = True
	if result:
		kw = {'users': result, 'len': len, 'clean': clean_html, 'follow': is_followed}
		return render_template('user.html', **kw)
	else:
		kw = {'result': '失败', 'code': '没有找到用户'}
		return render_template('result.html', **kw)


@app.route('/user_articles/<user_id>')
def all_articles(user_id):
	result = User.query.filter(User.id == user_id).first()
	if result:
		kw = {'users': result, 'clean': clean_html}
		return render_template('user_all_article.html', **kw)
	else:
		kw = {'result': '失败', 'code': '没有找到用户'}
		return render_template('result.html', **kw)


@app.route('/user_essays/<user_id>')
def all_essays(user_id):
	result = User.query.filter(User.id == user_id).first()
	if result:
		kw = {'users': result}
		return render_template('user_all_essays.html', **kw)
	else:
		kw = {'result': '失败', 'code': '没有找到用户'}
		return render_template('result.html', **kw)


@app.route('/newarticle', methods=['GET', 'POST'])
def new_article():
	if request.method == 'GET':
		if hasattr(g, 'user'):
			return render_template('new_article.html')
		else:
			return redirect(url_for('login'))
	else:
		new_title = request.form.get('title')
		new_content = request.form.get('content')
		if new_title and new_content:
			time_now = get_time()
			new_content = md2html(new_content)
			new_articles = Article(title=new_title, content=new_content, author_id=g.user.id, time=time_now)
			db.session.add(new_articles)
			db.session.commit()
			return redirect(url_for('article', article_id=new_articles.id))
		else:
			return render_template('publishfail.html', failcode='文章内容或标题不能为空')


@app.route('/newessay', methods=['GET', 'POST'])
def new_essays():
	if request.method == 'GET':
		if hasattr(g, 'user'):
			return render_template('new_essays.html')
		else:
			return redirect(url_for('login'))
	else:
		new_content = request.form.get('essays')
		if new_content:
			time_now = get_time()
			new_essay = Essays(content=new_content, author_id=g.user.id, time=time_now)
			db.session.add(new_essay)
			db.session.commit()
			return redirect(url_for('essays'))
		else:
			return render_template('publishfail.html', failcode='随笔文章内容为空')


@app.route('/delete_essay/<essay_id>')
def delete_essay(essay_id):
	result = Essays.query.filter(Essays.id == essay_id).first()
	if result:
		if g.user == result.author:
			db.session.delete(result)
			db.session.commit()
			kw = {'result': '删除成功', 'code': ''}
			return render_template('result.html', **kw)
		else:
			kw = {'result': '删除失败', 'code': '失败原因:没有权限'}
			return render_template('result.html', **kw)
	else:
		kw = {'result': '删除失败', 'code': '失败原因:没有找到这篇随笔'}
		return render_template('result.html', **kw)


@app.route('/delete_article/<article_id>')
def delete_article(article_id):
	result = Article.query.filter(Article.id == article_id).first()
	if result:
		if g.user == result.author:
			db.session.delete(result)
			db.session.commit()
			kw = {'result': '删除成功', 'code': ''}
			return render_template('result.html', **kw)
		else:
			kw = {'result': '删除失败', 'code': '失败原因:没有权限'}
			return render_template('result.html', **kw)
	else:
		kw = {'result': '删除失败', 'code': '失败原因:没有找到这篇随笔'}
		return render_template('result.html', **kw)


@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):
	result = Comment.query.filter(Comment.id == comment_id).first()
	if result:
		if g.user == result.author:
			db.session.delete(result)
			db.session.commit()
			kw = {'result': '删除成功', 'code': ''}
			return render_template('result.html', **kw)
		else:
			kw = {'result': '删除失败', 'code': '失败原因:没有权限'}
			return render_template('result.html', **kw)
	else:
		kw = {'result': '删除失败', 'code': '失败原因:没有找到这篇随笔'}
		return render_template('result.html', **kw)


@app.route('/follow/<user_id>')
def follow(user_id):
	result = User.query.filter(User.id == user_id).first()
	if result:
		if hasattr(g, 'user'):
			result = Follow.query.filter(Follow.followed_id == user_id, Follow.following_id == g.user.id).first()
			if not result:
				temp = Follow(following_id=g.user.id, followed_id=user_id)
				db.session.add(temp)
				db.session.commit()
				kw = {'result': '关注成功', 'code': ''}
			else:
				kw = {'result': '关注失败', 'code': '失败原因:已经关注过此用户'}
		else:
			kw = {'result': '关注失败', 'code': '失败原因:没有权限'}
	else:
		kw = {'result': '删除失败', 'code': '失败原因:没有找到这个用户'}
	return render_template('result.html', **kw)


@app.route('/follow_list/<user_id>')
def follow_list(user_id):
	users = User.query.filter(User.id == user_id).first()
	if users:
		user_list = []
		result = Follow.query.filter(Follow.following_id == user_id)
		print(result)
		if result:
			for temp in result:
				temp_result = User.query.filter(User.id == temp.followed_id).first()
				user_list.append(temp_result)
		return render_template('follow_list.html', result=user_list, len=len, users=users)
	else:
		kw = {'result': '查看失败', 'code': '失败原因:没有找到这个用户'}
		return render_template('result.html', **kw)


@app.route('/cancel_follow/<user_id>')
def cancel_follow(user_id):
	users = User.query.filter(User.id == user_id).first()
	if users:
		if hasattr(g, 'user'):
			result = Follow.query.filter(Follow.followed_id == user_id, Follow.following_id == g.user.id).first()
			if result:
				db.session.delete(result)
				db.session.commit()
				kw = {'result': '取消关注成功', 'code': ''}
			else:
				kw = {'result': '取消失败', 'code': '失败原因:你还没有关注他'}
		else:
			kw = {'result': '取消失败', 'code': '失败原因:没有权限'}
	else:
		kw = {'result': '取消失败', 'code': '失败原因:没有找到这个用户'}
	return render_template('result.html', **kw)


if __name__ == '__main__':
	app.run()
