from flask import Flask, render_template, redirect, request, session
import csv
import random
import requests
import vk_api
import os

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
    return render_template("home.html", person=person, user=user)

# @app.route('/process_swipe_left')
# def process_swipe_left():
#     print("Swiping Left")
#     return("nothing")

# @app.route('/process_swipe_right')
# def process_swipe_right():
#     print("Swiping Right")
#     return("nothing")

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
    