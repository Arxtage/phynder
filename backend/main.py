from flask import Flask, render_template
import csv
import random
import requests
import config

# vk uses only port 80, redirecting:
# sudo ncat --sh-exec "ncat 127.0.0.1 80" -l 5000 --keep-open
#
#

app = Flask(__name__)

VK_API_ID = 7534914
@app.route("/")
def home():
    # randomly select a movie
    with open('vk_phystech.csv') as f:
        reader = csv.reader(f)
        row = random.choice(list(reader))

    person = {
        'id': row[1],
        'name': row[2],
        'surname': row[3],
        'sex': row[6],
        'image': eval(row[8])['photo']['sizes'][-1]['url'],
   }
   
   

    # fetch cover image
    # call OMDB database
    #url = f"http://www.omdbapi.com/?t={movie['title']}/&apikey={config.api_key}"
    # get back the response
    #response = requests.request("GET", url)
    # parse result into JSON and look for matching data if available
    #movie_data = response.json()
    #if 'Poster' in movie_data:
    #    movie['image'] = movie_data['Poster']
    ##if 'imdbRating' in movie_data:
    #    movie['imdb'] = movie_data['imdbRating']
    # send all this data to the home.html template
    
    return render_template("home.html", person=person)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)