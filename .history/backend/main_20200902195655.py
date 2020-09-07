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
# DB_ROOT_DIR = '/Users/izakharkin/Desktop/skoltech/vrarhaptics/deepjest/phynder/backend/static/db'
DB_ROOT_DIR = '/Users/inarm/Desktop/PHYNDER.tmp/phynder/backend/static/db'
PATH_BOYS_CSV = f'{DB_ROOT_DIR}/boys.csv'
PATH_GIRLS_CSV = f'{DB_ROOT_DIR}/girls.csv'

PATH_BOYS_SWIPE_DIR= f'{DB_ROOT_DIR}/boys'
PATH_GIRLS_SWIPE_DIR= f'{DB_ROOT_DIR}/girls'

boys = pd.read_csv(PATH_BOYS_CSV)
girls = pd.read_csv(PATH_GIRLS_CSV)

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
            bttnredirect=url
        )
    else:
        return redirect('/swipes')

    
@app.route("/about")
def about():
    return render_template(
        "about.html", 
        user=session['user_id']
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
    res = redirect('/swipes')

    return res

def sample_partners_v2(user_id):
    """СЕРВЕР"""
    """Pick 20 partners to send for swipes"""

    #swipe_data = pd.read_csv(PATH_SWIPE_DATA_V2)

    if int(user_id) in boys.id.values:
        user_swipe_data_path = PATH_BOYS_SWIPE_DIR + '/{0}.csv'.format(user_id)
        user_swipe_data = pd.read_csv(user_swipe_data_path)
        sample = girls[~girls.id.isin(user_swipe_data.id_swiped)].sample(1)
        print("==========LEN OF DB WITH PEOPLE LEFT==========", len(girls[~girls.id.isin(user_swipe_data.id_swiped)]))
    elif int(user_id) in girls.id.values:
        user_swipe_data_path = PATH_GIRLS_SWIPE_DIR + '/{0}.csv'.format(user_id)
        user_swipe_data = pd.read_csv(user_swipe_data_path)
        sample = boys[~boys.id.isin(user_swipe_data.id_swiped)].sample(1)

    return(sample.to_json(orient='records'), user_swipe_data_path, user_swipe_data)


@app.route('/swipes')
def swipes():
    """ЮЗЕР?"""

    # check if logged, if not -> redirect to /login
    if 'access_token' not in session:
        url = '/login'
        return render_template(
            "index.html", 
            bttnredirect=url
                    )
    
    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0]
    session['sample'], user_swipe_data_path, user_swipe_data = sample_partners_v2(user_id)

    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[0] # one partner
    print('==========PARTNER_ID===========',partner['id'])
    person = {
        'id': partner['id'],
        'name': partner['first_name'],
        'surname': partner['last_name'],
        'sex': partner['sex'],
        'image': partner['crop_photo']
    }
    return render_template(
        "home.html", 
        person=person, 
        user=user_info
    )


@app.route('/swipes_new', methods = ['POST'])
def swipes_new():
    """Returns the new person for the next swipe."""
    
    # check if logged, if not -> redirect to /login
    if 'access_token' not in session:
        url = '/login'
        return render_template(
            "index.html",
            bttnredirect=url
        )

    access_token = session['access_token']

    user_id = session['user_id']
    user_info = vk_api.get_user_data(access_token, user_id)[0]
    session['sample'], user_swipe_data_path, user_swipe_data = sample_partners_v2(user_id)

    swipe_type = request.form['swipe_type']
    swipe_id = request.form['swipe_id']

    with open(user_swipe_data_path,'a') as fd:
        fd.write('\n{0},{1}'.format(swipe_id, swipe_type))


    #user_swipe_data = user_swipe_data.append({'id_swiped':int(swipe_id), 'action':swipe_type}, ignore_index=True)
    #user_swipe_data.to_csv(PATH_SWIPE_DATA_V2, index=False)

    list_of_dicts_of_partners = json.loads(session['sample'])
    partner = list_of_dicts_of_partners[0]
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
    