""" Module using VK API to get user's data"""

import requests

APP_URL = 'localhost'
VK_APP_ID = '7534914'
VK_APP_SECRET = '9NX0uGWfRtVSKEAyEWho'


def get_login_url():
    return "https://oauth.vk.com/authorize?client_id={0}&scope=friends,offline&redirect_uri=http://{1}/set_cookies&response_type=code".format(
        VK_APP_ID, APP_URL)


def get_access_token(code):
    access_token_link = "https://oauth.vk.com/access_token?client_id={0}&client_secret={1}&redirect_uri=http://{2}/set_cookies&code={3}".format(
        VK_APP_ID, VK_APP_SECRET, APP_URL, code)
    print("code: ", code)
    data = requests.get(url = access_token_link).json()
    access_token = data['access_token']
    user_id = data['user_id']
    return (access_token, str(user_id))


def get_user_data(access_token, user_ids):
    test_request = "https://api.vk.com/method/users.get?&v=5.102&access_token={0}&user_ids={1}".format(
        access_token, user_ids)
    data = requests.get(url = test_request).json()
    data = data['response']
    return data