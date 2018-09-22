from flask import Flask, url_for, render_template, redirect, session, g, request, jsonify
from models import *
import config
from check_code import get_check_code
import os
import time
from mistune import markdown
from clean_html import clean_html
import re
import datetime
import random

# from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(config)
app.config['SECRET_KEY'] = os.urandom(24)
# CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()

path_list = []


def check_mobile(request):
    userAgent = request.headers['User-Agent']
    # userAgent = env.get('HTTP_USER_AGENT')

    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(userAgent) != None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False


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
    if check_mobile(request):
        return render_template('index_mobile.html')
    else:
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


# @app.route('/tags')
# def tags():
#     result = Plate.query.all()
#     kw = {'plate': result, 'length': len(result)}
#     return render_template('tags.html', **kw)

#
# @app.route('/message')
# def message():
#     result = Message.query.all()
#     result = result[::-1]
#     kw = {'messages': result, 'length': len(result)}
#     return render_template('message.html', **kw)


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
            new_content = md2html(new_content)
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


@app.route('/api/login', methods=['POST'])
def api_login():
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
    username = request.json.get('username')
    temp_user = User.query.filter(User.username == username).first()
    if temp_user:
        if temp_user.password == request.json.get('password'):
            session['username'] = temp_user.username
            if request.json.get('isRemember'):
                session.permanent = True
            like_articles_id = []
            like_essays_id = []
            like_secrets_id = []
            like_articles = temp_user.like_articles
            like_essays = temp_user.like_essays
            like_secrets = temp_user.like_secrets
            for i in like_articles:
                like_articles_id.append(i.id)
            for i in like_essays:
                like_essays_id.append(i.id)
            for i in like_secrets:
                like_secrets_id.append(i.id)
            data = {
                'isLogin': True,
                'username': temp_user.username,
                'userID': temp_user.id,
                'likeArticles': like_articles_id,
                'likeEssays': like_essays_id,
                'likeSecrets': like_secrets_id
            }
        else:
            data = {'username': '', 'userID': 0, 'isLogin': False, 'failCode': '密码错误'}
    else:
        data = {'username': '', 'userID': 0, 'isLogin': False, 'failCode': '没有找到用户'}
    resp = jsonify(data)
    return resp


@app.route('/api/register', methods=['GET', 'POST'])
def api_register():
    global path_list
    if request.method == 'GET':
        try:
            session.pop('check_code')
        except KeyError:
            print('未发现session:check_code')
        check_code, md5, path = get_check_code()
        path_list.append(path)
        session['check_code'] = check_code
        data = {'md5': md5, 'url': '/static/image/code/code' + path + '.jpg'}
        resp = jsonify(data)
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        check_code = session.get('check_code')
        username = request.json.get('username')
        password = request.json.get('password')
        password_repeat = request.json.get('rePassword')
        if username and password and password_repeat:
            if check_code == request.json.get('check_code').lower():
                temp_user = User.query.filter(User.username == username).first()
                if temp_user:
                    # return render_template('registerfail.html', failcode='用户名已存在')
                    data = {'registerState': False, 'failCode': '用户名已存在'}
                else:
                    temp_user = User(username=username, password=password)
                    db.session.add(temp_user)
                    db.session.commit()
                    data = {'registerState': True}
                # data = {'registerState': True}
            else:
                data = {'registerState': False, 'failCode': '验证码错误'}
        else:
            data = {'registerState': False, 'failCode': '用户名或密码不能为空'}
        resp = jsonify(data)
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route('/api/logout')
def api_logout():
    session.clear()
    data = {'isLogout': True}
    resp = jsonify(data)
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/article/<article_id>')
def api_article(article_id):
    article_item = Article.query.filter(Article.id == article_id).first()
    comment_model = article_item.comment
    comments = []
    print(article_item.like)
    for i in comment_model:
        temp = {
            'content': i.content,
            'author': i.author.username,
            'time': i.time
        }
        comments.append(temp)
    data = {'title': article_item.title,
            'author': article_item.author.username,
            'authorID': article_item.author.id,
            'content': article_item.content,
            'like': len(article_item.like),
            'time': article_item.time,
            'comment': comments,
            'id': article_item.id
            }
    return jsonify(data)


# @app.route('/api/essay/<essay_id>')
# def api_essay(essay_id):
#     essay_item = Essays.query.filter(Essays.id == essay_id).first()
#     liked_users = essay_item.like,
#     isLiked = False
#     if hasattr(g, 'user'):
#         for user in liked_users:
#             if user == g.user:
#                 isLiked = True
#                 break
#     data = {
#             'author': essay_item.author.username,
#             'authorID': essay_item.author.id,
#             'content': essay_item.content,
#             'like': len(liked_users),
#             'time': essay_item.time,
#             'isLiked': isLiked
#             }
#     return jsonify(data)


@app.route('/api/secret/<secret_id>')
def api_secret(secret_id):
    secret_item = Secret.query.filter(Secret.id == secret_id).first()
    comment_model = secret_item.comment
    comments = []
    for i in comment_model:
        temp = {
            'content': i.content,
            # 'author': i.author.username,
            'time': i.time
        }
        comments.append(temp)
    data = {
        'title': secret_item.title,
        'content': secret_item.content,
        'like': len(secret_item.like),
        'time': secret_item.time,
        'comment': comments,
        'id': secret_item.id
    }
    return jsonify(data)


@app.route('/api/index')
def api_index():
    secret_item = Secret.query.order_by(db.desc(Secret.id)).first()
    article_item = Article.query.order_by(db.desc(Article.id)).first()
    essay_item = Essays.query.order_by(db.desc(Essays.id)).first()
    ArticleItem = {
        'title': article_item.title,
        'id': article_item.id,
        'author': article_item.author.username,
        'authorID': article_item.author.id,
        'content': clean_html(article_item.content)[0:200],
        'like': len(article_item.like),
        'time': article_item.time,
    }
    EssayItem = {
        'author': essay_item.author.username,
        'authorID': essay_item.author.id,
        'content': essay_item.content,
        'like': len(essay_item.like),
        'time': essay_item.time,
        'id': essay_item.id
    }
    SecretItem = {
        'id': secret_item.id,
        'title': secret_item.title,
        'content': clean_html(secret_item.content)[0:200],
        'like': len(secret_item.like),
        'time': secret_item.time,
    }
    data = {
        'SecretItem': SecretItem,
        'ArticleItem': ArticleItem,
        'EssayItem': EssayItem
    }
    return jsonify(data)


@app.route('/api/new_article', methods=['POST'])
def api_new_article():
    if hasattr(g, 'user'):
        new_title = request.json.get('title')
        new_content = request.json.get('articleContent')
        if new_title and new_content:
            time_now = get_time()
            new_content = md2html(new_content)
            new_article = Article(title=new_title, content=new_content, author_id=g.user.id, time=time_now)
            db.session.add(new_article)
            db.session.commit()
            data = {'isPublished': True, 'articleID': new_article.id}
        else:
            data = {'isPublished': False, 'failCode': '内容或标题不能为空'}
    else:
        data = {'isPublished': False, 'failCode': '登陆后才能发送内容'}
    return jsonify(data)


@app.route('/api/new_essay', methods=['POST'])
def api_new_essay():
    if hasattr(g, 'user'):
        new_content = request.json.get('articleContent')
        if new_content:
            time_now = get_time()
            new_content = md2html(new_content)
            new_essay = Essays(content=new_content, author_id=g.user.id, time=time_now)
            db.session.add(new_essay)
            db.session.commit()
            data = {'isPublished': True, 'articleID': new_essay.id}
        else:
            data = {'isPublished': False, 'failCode': '内容不能为空'}
    else:
        data = {'isPublished': False, 'failCode': '登陆后才能发送内容'}
    return jsonify(data)


@app.route('/api/new_secret', methods=['POST'])
def api_new_secret():
    if hasattr(g, 'user'):
        new_title = request.json.get('title')
        new_content = request.json.get('articleContent')
        if new_content:
            time_now = get_time()
            new_content = md2html(new_content)
            new_secret = Secret(title=new_title, content=new_content, author_id=g.user.id, time=time_now)
            db.session.add(new_secret)
            db.session.commit()
            data = {'isPublished': True, 'articleID': new_secret.id}
        else:
            data = {'isPublished': False, 'failCode': '内容不能为空'}
    else:
        data = {'isPublished': False, 'failCode': '登陆后才能发送内容'}
    return jsonify(data)


@app.route('/api/change_self_intro', methods=['GET', 'POST'])
def api_new_intro():
    if hasattr(g, 'user'):
        if request.method == 'GET':
            selfIntro = g.user.self_introduction
            if selfIntro:
                data = {'selfIntro': selfIntro}
            else:
                data = {'selfIntro': ''}
        else:
            new_self_intro = request.json.get('selfIntro')
            if new_self_intro:
                g.user.self_introduction = new_self_intro
                db.session.commit()
                data = {'isPublished': True}
            else:
                data = {'isPublished': False, 'failCode': '内容不能为空'}
    else:
        data = {'isPublished': False, 'failCode': '登陆后才能发送内容'}
    return jsonify(data)


@app.route('/api/mine')
def api_mine():
    if hasattr(g, 'user'):
        if g.user.self_introduction:
            data = {'selfIntro': g.user.self_introduction}
        else:
            data = {'selfIntro': g.user.self_introduction}
    else:
        data = {'error': 'error'}
    return jsonify(data)


@app.route('/api/user/<user_id>')
def api_user(user_id):
    temp_user = User.query.filter(User.id == user_id).first()
    if temp_user.articles:
        last_article = temp_user.articles[-1]
        last_article_data = {
            'title': last_article.title,
            'author': temp_user.username,
            'content': clean_html(last_article.content)[0:200],
            'like': len(last_article.like),
            'time': last_article.time,
            'id': last_article.id,
            'authorID': temp_user.id
        }
    else:
        last_article_data = False
    if temp_user.essays:
        last_essay = temp_user.essays[-1]
        last_essay_data = {
            'author': temp_user.username,
            'content': last_essay.content,
            'like': len(last_essay.like),
            'time': last_essay.time,
            'authorID': temp_user.id,
            'id': last_essay.id
        }
    else:
        last_essay_data = False
    if temp_user.self_introduction:
        data = {
            'username': temp_user.username,
            'selfIntro': temp_user.self_introduction,
            'lastArticle': last_article_data,
            'lastEssay': last_essay_data
        }
    else:
        data = {
            'username': temp_user.username,
            'selfIntro': '该用户来去无风，没有留下过签名~ ~ ~ ',
            'lastArticle': last_article_data,
            'lastEssay': last_essay_data
        }
    return jsonify(data)


@app.route('/api/user_articles/<user_id>')
def api_user_articles(user_id):
    temp_user = User.query.filter(User.id == user_id).first()
    articles = temp_user.articles
    params = request.values.to_dict()
    length = len(articles)
    article_list = []
    if length:
        if length > 10:
            if not len(params):
                params = {'start': 1, 'end': 10}
            noMore = False
        else:
            params = {'start': 1, 'end': length}
            noMore = True
        params['start'] = int(params['start'])
        params['end'] = int(params['end'])
        if length >= params['start']:
            if length > params['end']:
                for item in articles[::-1][params['start'] - 1:params['end']]:
                    temp = {
                        'author': item.author.username,
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': temp_user.id
                    }
                    article_list.append(temp)
            else:
                for item in articles[::-1][params['start'] - 1:length]:
                    temp = {
                        'author': item.author.username,
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': temp_user.id
                    }
                    article_list.append(temp)
                noMore = True
        else:
            noMore = True
    else:
        noMore = True
    data = {
        'ArticleList': article_list,
        'noMore': noMore,
        'username': temp_user.username
    }
    return jsonify(data)


@app.route('/api/user_essays/<user_id>')
def api_user_essays(user_id):
    temp_user = User.query.filter(User.id == user_id).first()
    essays = temp_user.essays
    params = request.values.to_dict()
    length = len(essays)
    essays_list = []
    if length:
        if length > 10:
            if not len(params):
                params = {'start': 1, 'end': 10}
            noMore = False
        else:
            params = {'start': 1, 'end': length}
            noMore = True
        params['start'] = int(params['start'])
        params['end'] = int(params['end'])
        if length >= params['start']:
            if length > params['end']:
                for item in essays[::-1][params['start'] - 1:params['end']]:
                    temp = {
                        'author': item.author.username,
                        'content': item.content,
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': temp_user.id,
                        'id': item.id
                    }
                    essays_list.append(temp)
            else:
                for item in essays[::-1][params['start'] - 1:length]:
                    temp = {
                        'author': item.author.username,
                        'content': item.content,
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': temp_user.id,
                        'id': item.id
                    }
                    essays_list.append(temp)
                noMore = True
        else:
            noMore = True
    else:
        noMore = True
    data = {
        'ArticleList': essays_list,
        'noMore': noMore,
        'username': temp_user.username
    }
    return jsonify(data)


@app.route('/api/articles')
def api_articles():
    articles = Article.query.all()
    params = request.values.to_dict()
    length = len(articles)
    article_list = []
    if length:
        if length > 10:
            if not len(params):
                params = {'start': 1, 'end': 10}
            noMore = False
        else:
            params = {'start': 1, 'end': length}
            noMore = True
        params['start'] = int(params['start'])
        params['end'] = int(params['end'])
        if length >= params['start']:
            if length > params['end']:
                for item in articles[::-1][params['start'] - 1:params['end']]:
                    temp = {
                        'author': item.author.username,
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': item.author.id
                    }
                    article_list.append(temp)
            else:
                for item in articles[::-1][params['start'] - 1:length]:
                    temp = {
                        'author': item.author.username,
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': item.author.id
                    }
                    article_list.append(temp)
                noMore = True
        else:
            noMore = True
    else:
        noMore = True
    data = {
        'ArticleList': article_list,
        'noMore': noMore
    }
    return jsonify(data)


@app.route('/api/essays')
def api_essays():
    essays = Essays.query.all()
    params = request.values.to_dict()
    length = len(essays)
    essays_list = []
    if length:
        if length > 10:
            if not len(params):
                params = {'start': 1, 'end': 10}
            noMore = False
        else:
            params = {'start': 1, 'end': length}
            noMore = True
        params['start'] = int(params['start'])
        params['end'] = int(params['end'])
        if length >= params['start']:
            if length > params['end']:
                for item in essays[::-1][params['start'] - 1:params['end']]:
                    temp = {
                        'author': item.author.username,
                        'content': item.content,
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': item.author.id,
                        'id': item.id
                    }
                    essays_list.append(temp)
            else:
                for item in essays[::-1][params['start'] - 1:length]:
                    temp = {
                        'author': item.author.username,
                        'content': item.content,
                        'like': len(item.like),
                        'time': item.time,
                        'authorID': item.author.id,
                        'id': item.id
                    }
                    essays_list.append(temp)
                noMore = True
        else:
            noMore = True
    else:
        noMore = True
    data = {
        'ArticleList': essays_list,
        'noMore': noMore,
    }
    return jsonify(data)


@app.route('/api/secrets')
def api_secrets():
    secrets = Secret.query.all()
    params = request.values.to_dict()
    length = len(secrets)
    secrets_list = []
    if length:
        if length > 10:
            if not len(params):
                params = {'start': 1, 'end': 10}
            noMore = False
        else:
            params = {'start': 1, 'end': length}
            noMore = True
        params['start'] = int(params['start'])
        params['end'] = int(params['end'])
        if length >= params['start']:
            if length > params['end']:
                for item in secrets[::-1][params['start'] - 1:params['end'] - 1]:
                    temp = {
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                    }
                    secrets_list.append(temp)
            else:
                for item in secrets[::-1][params['start'] - 1:length]:
                    temp = {
                        'title': item.title,
                        'id': item.id,
                        'content': clean_html(item.content)[0:200],
                        'like': len(item.like),
                        'time': item.time,
                    }
                    secrets_list.append(temp)
                noMore = True
        else:
            noMore = True
    else:
        noMore = True
    data = {
        'ArticleList': secrets_list,
        'noMore': noMore,
    }
    return jsonify(data)


@app.route('/api/islogin')
def api_is_login():
    if hasattr(g, 'user'):
        like_articles_id = []
        like_essays_id = []
        like_secrets_id = []
        like_articles = g.user.like_articles
        like_essays = g.user.like_essays
        like_secrets = g.user.like_secrets
        for i in like_articles:
            like_articles_id.append(i.id)
        for i in like_essays:
            like_essays_id.append(i.id)
        for i in like_secrets:
            like_secrets_id.append(i.id)
        data = {
            'isLogin': True,
            'username': g.user.username,
            'userID': g.user.id,
            'likeArticles': like_articles_id,
            'likeEssays': like_essays_id,
            'likeSecrets': like_secrets_id
        }
    else:
        data = {
            'isLogin': False,
        }
    return jsonify(data)


# @app.route('/api/like_article/<article_id>')
# def api_like_article(article_id):
#     if hasattr(g, 'user'):
#         article_item = Article.query.filter(Article.id == article_id)
#         g.user.like_articles.append(article_item)
#         db.session.commit()
#         data = {'success': True}
#     else:
#         data = {'success': False}
#     return jsonify(data)
#
#
# @app.route('/api/unlike_article/<article_id>')
# def api_unlike_article(article_id):
#     if hasattr(g, 'user'):
#         article_item = Article.query.filter(Article.id == article_id)
#         g.user.like_articles.pop(article_item)
#         db.session.commit()
#         data = {'success': True}
#     else:
#         data = {'success': False}
#     return jsonify(data)
#
#
# @app.route('/api/like_essay/<essay_id>')
# def api_like_essay(essay_id):
#     if hasattr(g, 'user'):
#         essay_item = Essays.query.filter(Essays.id == essay_id)
#         g.user.like_essays.append(essay_item)
#         db.session.commit()
#         data = {'success': True}
#     else:
#         data = {'success': False}
#     return jsonify(data)
#
#
# @app.route('/api/unlike_essay/<essay_id>')
# def api_unlike_essay(essay_id):
#     if hasattr(g, 'user'):
#         essay_item = Essays.query.filter(Essays.id == essay_id)
#         g.user.like_essays.pop(essay_item)
#         db.session.commit()
#         data = {'success': True}
#     else:
#         data = {'success': False}
#     return jsonify(data)


@app.route('/api/new_comment/<article_id>', methods=['POST'])
def api_comment(article_id):
    if hasattr(g, 'user'):
        new_content = request.json.get('comment')
        if new_content:
            time_now = get_time()
            new_comment = Comment(content=new_content, author_id=g.user.id, time=time_now, article_id=article_id)
            db.session.add(new_comment)
            db.session.commit()
            data = {'isPublish': True}
        else:
            data = {'isPublish': False, 'failCode': '评论不能为空'}
    else:
        data = {'isPublish': False, 'failCode': '登陆才能发布评论'}
    return jsonify(data)


@app.route('/api/new_secret_comment/<secret_id>', methods=['POST'])
def api_secret_comment(secret_id):
    if hasattr(g, 'user'):
        new_content = request.json.get('comment')
        if new_content:
            time_now = get_time()
            new_comment = SecretComment(content=new_content, author_id=g.user.id, time=time_now, article_id=secret_id)
            db.session.add(new_comment)
            db.session.commit()
            data = {'isPublish': True}
        else:
            data = {'isPublish': False, 'failCode': '评论不能为空'}
    else:
        data = {'isPublish': False, 'failCode': '登陆才能发布评论'}
    return jsonify(data)


@app.route('/mobile')
def mobile():
    return render_template('index_mobile.html')


@app.route('/api/like_article/<article_id>')
def like_article(article_id):
    if hasattr(g, 'user'):
        article_item = Article.query.filter(Article.id == article_id).first()
        isLiked = False
        for i in article_item.like:
            if g.user == i:
                isLiked = True
                break
        if not isLiked:
            article_item.like.append(g.user)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '已经赞过了'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/like_essay/<essay_id>')
def like_essay(essay_id):
    if hasattr(g, 'user'):
        essay_item = Essays.query.filter(Essays.id == essay_id).first()
        isLiked = False
        for i in essay_item.like:
            if g.user == i:
                isLiked = True
                break
        if not isLiked:
            essay_item.like.append(g.user)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '已经赞过了'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/like_secret/<secret_id>')
def like_secret(secret_id):
    if hasattr(g, 'user'):
        secret_item = Secret.query.filter(Secret.id == secret_id).first()
        isLiked = False
        for i in secret_item.like:
            if g.user == i:
                isLiked = True
                break
        if not isLiked:
            secret_item.like.append(g.user)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '已经赞过了'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/unlike_article/<article_id>')
def unlike_article(article_id):
    if hasattr(g, 'user'):
        article_item = Article.query.filter(Article.id == article_id).first()
        isLiked = False
        count = 0
        for i in article_item.like:
            count += count
            if g.user == i:
                isLiked = True
                break
        if isLiked:
            article_item.like.pop(count)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '还没有赞过'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/unlike_secret/<secret_id>')
def unlike_secret(secret_id):
    if hasattr(g, 'user'):
        secret_item = Secret.query.filter(Secret.id == secret_id).first()
        isLiked = False
        count = 0
        for i in secret_item.like:
            count += count
            if g.user == i:
                isLiked = True
                break
        if isLiked:
            secret_item.like.pop(count)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '还没有赞过'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/unlike_essay/<essay_id>')
def unlike_essay(essay_id):
    if hasattr(g, 'user'):
        essay_item = Essays.query.filter(Essays.id == essay_id).first()
        isLiked = False
        count = 0
        for i in essay_item.like:
            count += count
            if g.user == i:
                isLiked = True
                break
        if isLiked:
            essay_item.like.pop(count)
            db.session.commit()
            data = {'success': True}
        else:
            data = {'success': False, 'failCode': '还没有赞过'}
    else:
        data = {'success': False, 'failCode': '登陆才能完成此操作'}
    return jsonify(data)


@app.route('/api/delete_essay/<essay_id>')
def api_delete_essay(essay_id):
    result = Essays.query.filter(Essays.id == essay_id).first()
    if result:
        if g.user == result.author:
            db.session.delete(result)
            db.session.commit()
            data = {'result': True, 'failCode': ''}
        else:
            data = {'result': False, 'failCode': '没有权限'}
    else:
        data = {'result': False, 'failCode': '没有找到这篇随笔'}
    return jsonify(data)


@app.route('/api/delete_article/<article_id>')
def api_delete_article(article_id):
    result = Article.query.filter(Article.id == article_id).first()
    if result:
        if g.user == result.author:
            db.session.delete(result)
            db.session.commit()
            data = {'result': True, 'failCode': ''}
        else:
            data = {'result': False, 'failCode': '没有权限'}
    else:
        data = {'result': False, 'failCode': '没有找到这篇随笔'}
    return jsonify(data)


@app.route('/api/upload_img', methods=['POST'])
def api_upload_img():
    if hasattr(g, 'user'):
        nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        randomNum = random.randint(0, 100)
        if randomNum <= 10:
            randomNum = str(0) + str(randomNum)
        uniqueNum = str(nowTime) + str(randomNum)
        img = request.files.get('image')
        if img:
            basedir = os.path.abspath(os.path.dirname(__file__))
            file_ext = '.' + img.filename.split('.')[-1]
            path = "/static/image/" + uniqueNum + file_ext
            file_path = basedir + path
            img.save(file_path)
            data = {'success': True, 'path': path}
        else:
            data = {'success': False, 'failCode': '没有发现图片文件'}
    else:
        data = {'success': False, 'failCode': '登陆才能上传图片'}
    return jsonify(data)


@app.route('/api/passwd', methods=['POST', 'GET'])
def api_passwd():
    global path_list
    if hasattr(g, 'user'):
        if request.method == 'GET':
            try:
                session.pop('check_code')
            except KeyError:
                print('未发现session:check_code')
            check_code, md5, path = get_check_code()
            path_list.append(path)
            session['check_code'] = check_code
            data = {'md5': md5, 'url': '/static/image/code/code' + path + '.jpg'}
        else:
            check_code = session.get('check_code')
            old_password = request.json.get('oldPassword')
            password = request.json.get('password')
            password_repeat = request.json.get('rePassword')
            if old_password and password and password_repeat:
                if check_code == request.json.get('check_code').lower():
                    if old_password == g.user.password:
                        if password == password_repeat:
                            g.user.password = password
                            db.session.commit()
                            data = {'success': True}
                        else:
                            data = {'success': False, 'failCode': '两次的输入的新密码不一样'}
                    else:
                        data = {'success': False, 'failCode': '旧密码错误'}
                else:
                    data = {'success': False, 'failCode': '验证码错误'}
            else:
                data = {'success': False, 'failCode': '所有对话框都不能为空'}
    else:
        data = {'success': False, 'failCode': '未登录'}
    return jsonify(data)


if __name__ == '__main__':
    app.run()
