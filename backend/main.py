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
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # !!! REMOVE IN PRODUCTION
csrf.init_app(app)
app.secret_key = os.urandom(24)

VK_API_ID = 7534914
DB_ROOT_DIR = '/Users/izakharkin/Desktop/skoltech/vrarhaptics/deepjest/phynder/backend/'
# DB_ROOT_DIR = '/Users/inarm/Desktop/PHYNDER.tmp/phynder/backend'
PATH_BOYS_CSV = f'{DB_ROOT_DIR}/boys.csv'
PATH_GIRLS_CSV = f'{DB_ROOT_DIR}/girls.csv'
PATH_SWIPE_DATA_V2 = f'{DB_ROOT_DIR}/swipe_data_v2.csv'


# helper function for Flask to use not cached but new verions of static files
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


@app.route("/")
@app.route('/index')
def home():
    """ Render main page if not authorized
        And redirect to page with swipes if authorized
    """
    if 'access_token' not in session:
        url = '/login'
        return render_template(
            "index.html", 
            bttnredirect=url,
            last_updated=dir_last_updated('static')
        )
    else:
        return redirect('/swipes')

    
@app.route("/about")
def about():
    return render_template(
        "about.html", 
        user=session['user_id'], 
        last_updated=dir_last_updated('static')
    )


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
    res = redirect('/swipes')

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

    boys = pd.read_csv(PATH_BOYS_CSV)
    girls = pd.read_csv(PATH_GIRLS_CSV)
    swipe_data = pd.read_csv(PATH_SWIPE_DATA_V2)

    if int(user_id) in boys.id.values:
        # проверка какие девочки уже находятся в id_swiped для user_id и семпл из тех, кого там нет
        sample = girls[~girls.id.isin(swipe_data[swipe_data.id == int(user_id)].id_swiped)].sample(1)
    elif int(user_id) in girls.id.values:
        sample = boys[~boys.id.isin(swipe_data[swipe_data.id == int(user_id)].id_swiped)].sample(1)

    return(sample.to_json(orient='records'), swipe_data)


@app.route('/swipes')
def swipes():
    """ЮЗЕР?"""

    # check if logged, if not -> redirect to /login
    if 'access_token' not in session:
        url = '/login'
        return render_template(
            "index.html", 
            bttnredirect=url, 
            last_updated=dir_last_updated('static')
        )
    
    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0]  # убрать в серверную часть
    
    #num = session['partner_counter']
    session['sample'], swipe_data = sample_partners_v2(user_id)
    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[0]
    print('==========PARTNER_ID===========',partner['id'])
    person = {
        'id': partner['id'],
        'name': partner['first_name'],
        'surname': partner['last_name'],
        'sex': partner['sex'],
        'image': partner['crop_photo']
    }

    #session['partner_counter'] += 1
    #print(session['partner_counter'])
    return render_template(
        "home.html", 
        person=person, 
        user=user_info,
        last_updated=dir_last_updated('static')
    )


@app.route('/swipes_new', methods = ['POST'])
def swipes_new():
    """Returns the new person for the next swipe."""
    
    # check if logged, if not -> redirect to /login
    if 'access_token' not in session:
        url = '/login'
        return render_template(
            "index.html", 
            bttnredirect=url,
            last_updated=dir_last_updated('./static')
        )

    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0]  # убрать в серверную часть

    session['sample'], swipe_data = sample_partners_v2(user_id)
    
    swipe_type = request.form['swipe_type']
    swipe_id = request.form['swipe_id']

    swipe_data = swipe_data.append({'id':int(user_id), 'id_swiped':int(swipe_id), 'action':swipe_type}, ignore_index=True)
    swipe_data.to_csv(PATH_SWIPE_DATA_V2, index=False)

    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[0]
    #print('==========PARTNER_ID===========',partner['id'])
    person = {
        'id': partner['id'],
        'name': partner['first_name'],
        'surname': partner['last_name'],
        'sex': partner['sex'],
        'image': partner['crop_photo']
    }

    return person


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    