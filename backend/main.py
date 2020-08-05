from flask import Flask, render_template, redirect, request, session
import csv
import random
import requests
import vk_api
import os


app = Flask(__name__)
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
        return redirect('/swipes')

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
    """ Get access token and set the cookie with it """
    global code
    code = request.args.get('code')
    access_token, user_id = vk_api.get_access_token(code)
    session['access_token'] = access_token
    session['user_id'] = user_id

    res = redirect('/swipes')
    return res

@app.route('/swipes')
def swipes():

    access_token = session['access_token']
    user_id = session['user_id']
    user = vk_api.get_user_data(access_token, user_id)[0]

    # TODO choose 20 swipe options instead of random 
    # randomly select a movie
    with open('vk_phystech.csv') as f:
        reader = csv.reader(f)
        row = random.choice(list(reader))

        person = {
            'id': row[1],
            'name': row[2],
            'surname': row[3],
            'sex': row[6],
            'image': eval(row[8])['photo']['sizes'][-1]['url']
            }    
    return render_template("home.html", person=person, user = user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)