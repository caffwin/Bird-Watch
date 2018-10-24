
from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)
from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
from random import randint
from model import Bird, User, Favorite, Checklist, connect_to_db, db

import requests 

import os
import time
import json

# from passlib.hash import sha_256_crypt

# Assign password; 
# password = sha256+crypt.encrypt("password")

# When logging in, apply same thing:
# password = sha256+crypt.encrypt("password")

#######################################################################
# import hashlib, uuid

# password = 'test_password'
# salt = uuid.uuid4().hex

# t_sha = hashlib.sha512()
# t_sha.update(password+salt)
# hashed_password = hashlib.sha512(password + salt).hexdigest()

# store hashed password in db


# print("PASSWORD: ")
# print(password)
# print("SALT: ")
# print(salt)
# print("HASHED_PASSWORD: ")
# print(hashed_password)


UPLOAD_FOLDER = 'static/user_pics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 500 * 500

app.secret_key = "secret_key"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage"""
    user = User.query.get(session['user_id'])
    bird = Bird.query.first()

    birds_total = len(Bird.query.all()) # int of 6

    # print("TYPE OF DATA FOR BIRD QUERY ALL")
    # print(type(Bird.query.all()))

    # print("TYPE OF BIRDS TOTAL VAR")
    # print(type(birds_total))

    # print("LENGTH OF LEN BIRD QUERY")
    # print(len(Bird.query.all()))

    ran_bird = randint(1, len(Bird.query.all()))
    bird = Bird.query.get(ran_bird)

    # # print("RANDOMIZED BIRD NUMBER IS.. ")
    # # print(ran_bird)

    # print("BIRD IS..")
    # print(bird)
    # print(type(bird)) # bird is a class


    if 'user_id' in session:
        print('You are logged in as ' + str(session['user_id']))
        flash('You are now logged in!')

    else:
        print('No one is currently logged in.')


    return render_template('homepage.html', bird=bird, user=user)
    # return render_template('homepage.html', user=user, bird=bird)


@app.route('/login', methods=['GET'])
def login_form():

    return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login_process():

    # Users may use email OR username to log in
    login_id = request.form.get('login_id') #jhacks
    password = request.form.get('password') #jhacks
    # password = hashlib.sha512(password + salt).hexdigest()
    # The password input is hashed to match hashed pw in db
    user = User.query.filter(User.email == login_id).first()

    if not user:
        user = User.query.filter(User.username == login_id).first()
    
    if user:
        if user.password == password:
            print("Password matches username!")
            flash("Logged in")
            session['user_id'] = user.user_id # saves to session
            # return redirect('/users/{}'.format(user.user_id))
            return redirect('/users/my_page')
            # Redirect here instead for personal feed
        # elif user.password == None:
        #     return redirect('/')

        else: 
            print("Password does not match user!")
            flash("Incorrect Password")
            # This happens when username typed, password blank

    else: 
        print("User not found! Please try again, or register.")
        flash("User not found! Please try again, or register.")
        return redirect('/')


@app.route('/register', methods=['GET'])
def registration_form():

    return render_template('register_page.html')

@app.route('/register', methods=['POST'])
def registration_process():

    username = request.form.get('reg_username')
    email = request.form.get('reg_email')
    password = request.form.get('reg_pw')
    # password = hashlib.sha512(password + salt).hexdigest()
    # The password ENTERED is hashed
    fname = request.form.get('reg_fname')
    lname = request.form.get('reg_lname')

    # Check that user var matches an entry in db
    user = User.query.filter(User.email == email).first()

    if user == None: # If user doesn't exist in db
        # Add user to db
        print("User added!")
        flash("User added!")

        user = User(username=username, password=password, email=email, fname=fname, lname=lname)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

    else:
        print("This user already exists! Please log in.")
        flash("This user already exists! Please log in.")

    # return redirect('/users/{}'.format(user.user_id))
    return redirect('/')
    # Redirect to home page


@app.route('/logout')
def logout_process():
    """Logs user out from website"""
    del session['user_id']
    return redirect('/')


@app.route('/users/my_page')
def user_feed():

    user = User.query.get(session['user_id'])
    # favorite = Favorite.query.filter(Favorite.user_id == session['user_id']).all()
    # print("favorite is " + str(favorite))

    print("The session ID is: " + str(session['user_id']))
    # [User ID: 1, Bird ID: 2, User ID: 1, Bird ID: 5]

    print("User faves " + str(user.favorites))
    # [User ID: 1, Bird ID: 2, User ID: 1, Bird ID: 5]

    print("User ID " + str(user.user_id))
    # User ID 1

    # print("User ID from favorites " + str(user.favorites.user_id))
    # randomize a bird from the birds list and return
    # the *th element (url)

    # total_birds = len(Bird.query.all())
    # print(total_birds)

    # for i in range(len(total_birds))
    # random_num = randint()
    # bird_pic = Bird.query.get(bird.image).first()

    if user.image_name:
        user.image_name = str(user.image_name) + '?{}'.format( str(time.time()) )


    print("USER.IMAGE_NAME IS: ")
    print(user.image_name)

    return render_template('my_page.html', user=user)

# https://www.flickr.com/photos/{owner}/{id}


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("users_list.html", users=users)


@app.route('/users/<user_id>')
def show_user_profile(user_id):
    """Shows specific user's profile"""
    user = User.query.get(user_id)
    return render_template('user_profile.html', user=user)


@app.route('/user_settings')
def show_user_settings():

    user = User.query.get(session['user_id'])
    # user_pw = User.query.filter
    # 
    # db.session.commit()
    return render_template('user_settings.html', user=user)


# @app.route('/user/settings', methods=['POST'])
# def change_user_settings():


# flickr
# @app.route('/botd_info.json')
# def get_img_from_api():

#     key = os.environ['flickr_api_key']
#     secret = os.environ['flickr_secret']


#     URL = 'https://api.flickr.com/services/rest/'

#     url_start = 'www.flickr.com/photos/'
#     params2 = {
#     'group_id': '1988039@N24'
#     'image_id': "29999296887"
#     }

#     image_url = url_start 


#     params = {
#     'method': 'flickr.groups.pools.getPhotos',
#     'api_key': key,
#     'group_id': '1988039@N24',
#     'page': 1,
#     'per_page': 2,
#     'format': 'json',
#     }
#     r = requests.get(url = URL, params = params)


#     text = r.text 
#     prefix = 'jsonFlickrApi('
#     text = text[text.startswith(prefix) and len(prefix) : -1]
#     json_result = json.loads(text)
    
#     print(type(json_result))
    
#     print(json_result)
#     return jsonify(text)

@app.route('/birds.json')
def get_birds_from_api():  

    lat = request.args.get('globalLat')
    lng = request.args.get('globalLng')
    key = os.environ['ebird_api_key']

    print("LAT IS: ")
    print(lat)
    print("LNG IS: ")
    print(lng)
    # 
    params = {'lat': lat,
    'lng': lng, 
    'key': key
    }

    URL = 'https://ebird.org/ws2.0/data/obs/geo/recent?'
    r = requests.get(url = URL, params = params)

    print(type(r))
    data = r.json()
    print("DATA: ")
    print(data)
    print("DATA TYPE: ")
    print(type(data))
    print("ZEROTH INDEX OF DATA: ")
    # print(data[0])
    return jsonify(data)

@app.route('/upload', methods=['POST'])
def upload_file():
    user = User.query.get(session['user_id'])
    # check if the post request has the file part

    file = request.files['upload-image']
    # if 'upload-image' not in request.files:
    #     flash('No file part')
    #     return redirect('/user/my_page')

    # if user does not select file, browser also
    # submit an empty part without filename
    # if file.filename == '':
    #     flash('No selected file')
    #     return redirect('users/my_page')
    # if file and allowed_file(file.filename):
    image_name = None

    if file.filename == '':
        # Fix this 
        flash("could not save image")
        return redirect('/users/my_page')
    
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']) + '_profile.jpg'))
    print("FILE IS: ")
    print(file)
    print("FILENAME IS:")
    print(filename)


    image_name = str(session['user_id']) + '_profile.jpg'

    user.image_name = image_name
    db.session.commit()

    return redirect('/users/my_page')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['static/user_pics'],
                               filename)


@app.route('/birds_list')
def birds_list():
    """Show list of birds."""

    birds = Bird.query.all()
    return render_template("birds_list.html", birds=birds)


# @app.route('/update_user_settings', methods=['POST'])
# def change_user_info():


@app.route('/birds/<bird_id>')
def view_birds(bird_id):
#     """Show details of a specific bird."""
    user = User.query.get(session['user_id'])
    # print("THE USER IS: ")
    # print(user)
    # print(user.user_id)
    # returns user object
    bird = Bird.query.get(bird_id) # bird by bird_id
    # print("THE BIRD IS:")
    # print(bird)
    favorite = Favorite.query.all()
    user_fave = Favorite.query.filter((Favorite.user_id == session['user_id']), (Favorite.bird_id == bird_id)).first()


    
    if user_fave:
        print("Hi! This bird is a user favorite.")
    else: 
        print("USER DOES NOT LIKE THIS BIRD. SHAME ON THEM.")

    return render_template("bird_page.html", bird=bird, user_fave=user_fave, user=user)


# make fave route with post request
@app.route('/favorite/<bird_id>') #methods=['POST']
def add_remove_favorite(bird_id):
    """Adds or removes bird from favorites table"""
    bird_id = request.args.get('bird_id')
    print('we are going to favorite a bird with id {}'.format(bird_id))
    user = User.query.get(session['user_id'])

    # bird_id = request.form.get('') # this is part of the url 
    # user_id = request.form.get('') # This is the name of the user from session[user_id]
    # user = request.form.get('') # The user is the user
    # bird = request.form.get('') # This is the bird whose page you're 

    favorite = Favorite(bird_id=bird_id, user_id=user_id, user=user, bird=bird)
    favorite = Favorite.query.filter_by(bird_id=bird_id).get()

    # Check that user var matches an entry in db
    # user = User.query.filter(User.email == email).first()
    # favorite = Favorite.query.filter(Favorite.bird_id == bird.id).first()


    # if not favorite:
        # add 

        # if text is "favorite"/if button is clicked:
            # db.session.add(bird_id)
    # else: # if fave:
        # 


    # db.session.add(favorite)
    # db.session.delete(favorite)
    # db.session.commit()

    return redirect('/bird_page')



@app.route('/map')
def show_map():
    key = os.environ['google_maps_api_key']
    return render_template('map.html', key=key)

# @app.route('/map2')
# def show_map2():
#     key = os.environ['google_maps_api_key']
#     return render_template('map2.html', key=key)

@app.route('/user_location', methods=['POST'])
def getUserLocation():
    """Gets user location from text input (geocoding)"""

    latitude = request.form.get('latLocation')
    longitude = request.form.get('longLocation')

    user = User.query.get(session['user_id'])

    return redirect('/map')


if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')