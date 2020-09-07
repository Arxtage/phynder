from flask import Flask, render_template, redirect, request, session
import csv
import random
import requests
import vk_api
import os
import pandas as pd
import json
#from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)
app.secret_key = os.urandom(24)

VK_API_ID = 7534914


@app.route("/")
@app.route('/index')
def home():
    """ Render main page if not authorized
        And redirect to page with swipes if authorized
    """
    if 'access_token' not in session:
        url = '/login'
        return render_template("index.html", bttnredirect=url)
    else:
        return redirect('/swipes_new')

@app.route("/about")
def about():
    return render_template("about.html", user = session['user_id'])

@app.route('/login/')
def login():
    """ VK Auth and redirect to /set_cookies with vk code """
    login_url = vk_api.get_login_url()
    return redirect(login_url)

@app.route('/set_cookies')
def set_cookies():
    """СЕРВЕР"""
    """ Get access token and set the cookie with it """

    global code
    code = request.args.get('code')

    access_token, user_id = vk_api.get_access_token(code)
    session['access_token'] = access_token
    session['user_id'] = user_id
    #session['sample'] = sample_partners_v2(user_id)
    #session['partner_counter'] = 0
    res = redirect('/swipes_new')

    return res

# def sample_partners(user_id):
#     """СЕРВЕР"""
#     """Pick 20 partners to send for swipes"""

#     users_data = pd.read_csv('/Users/inarm/Desktop/PHYNDER.tmp/phynder/backend/ONE_IMG_vk_phystech.csv')
#     swipe_data = pd.read_csv('/Users/inarm/Desktop/PHYNDER.tmp/phynder/backend/swipe_data.csv')
#     user_combinations = swipe_data[swipe_data["id"]==int(user_id)]
#     sample = user_combinations[swipe_data['action'].isna()].sample(20)

#     df2 = users_data.loc[users_data['id'].isin(sample.swiped)]
#     merged = pd.merge(sample, df2, left_on='swiped', right_on='id')
#     return(merged.to_json(orient='records'))

def sample_partners_v2(user_id):
    """СЕРВЕР"""
    """Pick 20 partners to send for swipes"""

    boys = pd.read_csv('./boys.csv')
    girls = pd.read_csv('./girls.csv')
    swipe_data = pd.read_csv('./swipe_data_v2.csv')

    if int(user_id) in boys.id.values:
        # проверка какие девочки уже находятся в id_swiped для user_id и семпл из тех, кого там нет
        sample = girls[~girls.id.isin(swipe_data[swipe_data.id == int(user_id)].id_swiped)]#.sample(20)
    elif int(user_id) in girls.id.values:
        sample = boys[~boys.id.isin(swipe_data[swipe_data.id == int(user_id)].id_swiped)]#.sample(20)

    return(sample.to_json(orient='records'))

@app.route('/swipes')
def swipes():
    """ЮЗЕР?"""
    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0] #убрать в серверную часть
    
    #num = session['partner_counter']
    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[num]
    person = {
        'id': partner['id'],
        'name': partner['first_name'],
        'surname': partner['last_name'],
        'sex': partner['sex'],
        'image': partner['crop_photo']
    }

    #session['partner_counter'] += 1
    #print(session['partner_counter'])
    return render_template("home.html", person=person, user=user_info)

@app.route('/swipes_new', methods = ['POST'])
def swipes_new():
    """ЮЗЕР?"""
    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0] #убрать в серверную часть

    session['sample'] = sample_partners_v2(user_id)
    print('======SAMPLE====',session['sample'])
    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[num]
    person = {
        'id': partner['id'],
        'name': partner['first_name'],
        'surname': partner['last_name'],
        'sex': partner['sex'],
        'image': partner['crop_photo']
    }

    return person  # render_template("home.html", person=person, user=user_info)

@app.route('/post_swipe_left', methods = ['POST'])
def post_swipe_left():
#     jsdata1 = request.data
#     jsdata2 = request.name
    jsdata = request.form['swipe_data']
    print(jsdata)
    return('https://sun1-92.userapi.com/dnlKY5Ehvn6DBK69pIe9XARmfe0C68zjkggwBA/UJ5ZqW5sbbk.jpg')  # json.loads(jsdata)[0]

@app.route('/post_swipe_right', methods = ['POST'])
def post_swipe_right():
#     jsdata1 = request.data
#     jsdata2 = request.name
    jsdata = request.form['swipe_data']
    print(jsdata)
    return('https://sun9-15.userapi.com/c830409/v830409625/90304/v_bkC18PLrc.jpg')  # json.loads(jsdata)[0]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)