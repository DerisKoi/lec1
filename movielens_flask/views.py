# coding=utf-8
from  flask import render_template, Blueprint, redirect, url_for, flash
from run import login_manger
from forms import Login_Form, Register_Form, Recommond_Form
from models import Users, Movie
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required
from run import db
from datetime import datetime
from recommend import guess
import random

# Flask使用Blueprint让应用实现模块化
movie = Blueprint('movie', __name__)  # 蓝图

@movie.route('/')
def index():
    form = Login_Form()
    return render_template('login.html', form=form)


@movie.route('/login', methods=['GET', 'POST'])
def login():
    form = Login_Form()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user)
            flash(u'登录成功')
            return render_template('text.html', username=form.username.data, current_time=datetime.utcnow())
        else:
            flash(u'用户或密码错误')
            return render_template('login.html', form=form)


# 用户登出
@movie.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'你已退出登录')
    return redirect(url_for('movie.index'))


@movie.route('/register', methods=['GET', 'POST'])
def register():
    form = Register_Form()
    if form.validate_on_submit():
        user_Inquire = Users.query.filter_by(username=form.username.data).first()
        if user_Inquire is None:
            user = Users(username=form.username.data, password=form.password.data)
            # suiji_num = str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))
            db.session.add(user)
            db.session.commit()
            flash(u'注册成功')
            return redirect(url_for('movie.index'))
        else:
            flash(u"您已注册！需要登录？")
            return redirect(url_for('movie.index'))
    return render_template('register.html', form=form)


import time
@movie.route('/recommond', methods=['GET', 'POST'])
def recommond():
    form = Recommond_Form()
    movie_list = []
    movie_href_list = []
    movie_pic_list = []
    if form.validate_on_submit():
        # 获取表单id
        id = form.id.data
        #print id,type(id)
        flash(u'开始运行！正在处理数据，这可能需要等10秒...')
        # 得到推荐结果
        print('hahahahahaha')
        result = guess.run_recommond(id)
        print('result=', result[0])
        print('result.recommendations=', result[0]['recommendations'])
        #print(result.recommendations)
        for item in result[0]['recommendations']:
            # 获取title, movie_href 和 pic_href
            title, m_h, p_h = get_movie_pic_and_url(item[0])
            # 电影名称
            movie_list.append(title)
            movie_href_list.append(m_h)
            movie_pic_list.append(p_h)
            #print(item[0])

    num_type = len(movie_list)
    num_type_half = int(num_type/2)
    return render_template('recommond.html', form=form, df=movie_list, df2=movie_href_list, df3 = movie_pic_list, num = num_type, num_half = num_type_half)


# 从MySQL中根据title，获取url和pic
def get_movie_pic_and_url(movie_id):
    print('movie_id=', movie_id)
    rows = db.session.query(Movie.title, Movie.movie_href, Movie.pic_href).filter(Movie.movie_id == movie_id)
    movies = []
    for row in rows:
        movies.append(row)
    if len(movies) > 0:
        temp = movies[0] 
        #return movies[0]['movie_href'], movies[0]['pic_href']
        return temp.title, temp.movie_href, temp.pic_href
    else:
        return '', '', ''
