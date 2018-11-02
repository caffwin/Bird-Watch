from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)
from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
from random import randint
from model import Bird, User, Favorite, Checklist, connect_to_db, db

from sqlalchemy import update # Might not need this

import requests 

import os
import time
import json

import bcrypt

print(bcrypt)


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
    
    # bird = Bird.query.first()

    # birds_total = len(Bird.query.all()) # int of 6

    # # print("TYPE OF DATA FOR BIRD QUERY ALL")
    # # print(type(Bird.query.all()))

    # # print("TYPE OF BIRDS TOTAL VAR")
    # # print(type(birds_total))

    # # print("LENGTH OF LEN BIRD QUERY")
    # # print(len(Bird.query.all()))

    # ran_bird = randint(1, len(Bird.query.all()))
    # bird = Bird.query.get(ran_bird)

    # # print("RANDOMIZED BIRD NUMBER IS.. ")
    # # print(ran_bird)

    # print("BIRD IS..")
    # print(bird)
    # print(type(bird)) # bird is a class

    user = None

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        print('You are logged in as ' + str(session['user_id']))
        flash('You are now logged in!')
        print(user.fname)

    else:
        print('No one is currently logged in.')


    return render_template('homepage.html', user=user)
    # return render_template('homepage.html', bird=bird, user=user)
    # return render_template('homepage.html', user=user, bird=bird)


def get_hashed_password(plain_text_password):

    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):

    return bcrypt.checkpw(plain_text_password, hashed_password)


@app.route('/login')
def login_form():

    return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login_process():

    # Users may use email OR username to log in
    login_id = request.form.get('login_id') #jhacks
    password = request.form.get('password') #jhacks


    user = User.query.filter(User.email == login_id).first()

    if not user:
        user = User.query.filter(User.username == login_id).first()
    
    if user:
        check_pw = check_password(password, user.password)
        # if password = hashed_password
        if check_pw:
        # if user.password == password:
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
            return redirect('/')
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
    hashed_pw = get_hashed_password(password)

    # check to make sure user doesn't already exist before
    # allowing new entry to be made in DB

    fname = request.form.get('reg_fname')
    lname = request.form.get('reg_lname')

    # Check that user var matches an entry in db
    user = User.query.filter(User.email == email).first()

    if user == None: # If user doesn't exist in db
        # Add user to db
        print("User added!")
        flash("User added!")

        if username.isalnum() == True:
            print("Username alphanumeric!")
            flash("Username alphanumeric!")
        # user = User(username=username, password=hashed_pw, email=email, fname=fname, lname=lname)
            user = User(username=username, password=hashed_pw, email=email, fname=fname, lname=lname)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.user_id

        else:
            print("Please re-enter an alphanumeric password between 8-16 letters!")
            return redirect('/register')
    else: # user already exists in db
        print("This user already exists! Please log in.")
        flash("This user already exists! Please log in.")

    return redirect('/')
    

@app.route('/logout')
def logout_process():
    """Logs user out from website"""
    del session['user_id']
    return redirect('/')


@app.route('/users/my_page')
def user_feed():
    """Shows user's page (private), only viewable if logged in as user"""

    # print("User ID " + str(user.user_id))

    # print("User ID from favorites " + str(user.favorites.user_id))
    # randomize a bird from the birds list and return
    # the *th element (url)

    # total_birds = len(Bird.query.all())
    # print(total_birds)

    # for i in range(len(total_birds))
    # random_num = randint()
    # bird_pic = Bird.query.get(bird.image).first()
    # if user == None:
    #     return render_template('user_oops.html')

    # write edge case for user trying to access this page without being logged in

    if 'user_id' not in session:

        ## if something, get flash messages from ratings lab for flashes
        return render_template('user_oops.html')

    user = User.query.get(session['user_id'])

    if user: 
        if user.image_name:
            user.image_name = str(user.image_name) + '?{}'.format( str(time.time()) )

    print("USER.IMAGE_NAME IS: ")
    print(user.image_name)

    return render_template('my_page.html', user=user)


@app.route('/forgot_password')
def forget_password_page():
    """Forget password page, original - not considering email notification for reset"""
    """Old and will probably be deleted"""

    return render_template('forgot_password.html')

@app.route('/reset_password')
def reset_password():
    """Resets user's password after recieving email"""

    return render_template('reset_password.html')

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
    """Renders the user_settings.html page"""
    
    if 'user_id' not in session:
        return render_template('user_oops.html')

    user = User.query.get(session['user_id'])
    return render_template('user_settings.html', user=user)


@app.route('/birds.json')
def get_birds_from_api():  

    lat = request.args.get('globalLat')
    lng = request.args.get('globalLng')

    key = os.environ['ebird_api_key']
    
    print("Request args: ")
    print(request.args)
    print("LAT IS: ")
    print(lat)
    print("LNG IS: ")
    print(lng)
    
    params = {'lat': lat,
    'lng': lng 
    }

    headers = {
    'X-eBirdApiToken': key
    }

    URL = 'https://ebird.org/ws2.0/data/obs/geo/recent/'
    r = requests.get(url = URL, params = params, headers = headers)

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
    image_name = None

    if file.filename == '':
        # Fix this 
        flash("Oh no! Could not save image.")
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
    """Store filename in user_pics folder"""
    return send_from_directory(app.config['static/user_pics'],
                               filename)


@app.route('/about')
def about_page():

    return render_template("/about.html")


# This page won't exist, eventually.. unless it's a list of all birds that have been favorited
@app.route('/birds_list')
def birds_list():
    """Show list of birds."""

    birds = Bird.query.all()
    return render_template("birds_list.html", birds=birds)


@app.route('/update_user_settings', methods=['POST'])
def change_user_info():

    # Get new values
    new_username = request.form.get('upd_username')
    new_fname = request.form.get('upd_fname')
    new_lname = request.form.get('upd_lname')
    new_email = request.form.get('upd_email')
    new_pw = request.form.get('upd_pw')

    # if not new_pw: # if password field left blank..
    #     # don't update it 
    
    # if the "updated" value is the same as old value, db is smart and won't update
    if new_fname.isalnum():  #if an entry in our request.args dict exists:
        new_fname.strip()
        new.fname.lower()
        new.fname.title()
        user.fname = new_fname

    if new_lname:
        new_lname.strip()
        new.lname.lower()
        new.lname.title()
        user.lname = new_fname

    if new_username:
        new_username.strip()
        use.username = new_username

    if new_email:
        new_email.strip()
        new_email.lower()
        user.email = new_email

    # strip if no trailing white space
    # entire username alphanumeric (letters & nums)
    # make sure user can't submit empty form
    # validate that data exists
    # if changing username, change & log out


    # ask for old pw too, if correct and
    # if new_pw: 
    #     if new_pw == new_pw2: 
    #         pass
    #         # update
    #     else: 
    #         print("The passwords don't match! Try again")

    user = User.query.get(session['user_id'])

    print("USER'S OLD FIRST NAME IS: ")
    print(user.fname)
    print("USER'S FIRST NAME IS: ")
    print(new_fname)

    user.email = new_email
    user.fname = new_fname
    user.lname = new_lname
    new_hashed_pw = get_hashed_password(new_pw)

    user.username = new_username
    print("USER'S NEW FNAME IS: ")
    print(user.username)
    # user.password = new_hashed_pw


    db.session.commit()

    return redirect('/')


@app.route('/get_bird_page_data')
def get_bird_code_and_name():
    """Gets data of species_code and common name from map.html template"""

    species_code = request.args.get('speciesCode')
    # return render_template('/birds/' + species_code) returns this:
    # http://localhost:5000/get_bird_page_data?speciesCode=wesgul
    return redirect('/birds/' + species_code)


@app.route('/test_xc')
def get_xenocanto_json():

    # xc_URL = 'https://www.xeno-canto.org/api/2/recordings'

    xc_URL_canada = 'https://www.xeno-canto.org/api/2/recordings'



    for i in range(1, 16):

        xc_canada_params = {
        'query': 'cnt:canada',
        'page': i
        }
        r = requests.get(url=xc_URL_canada, params=xc_canada_params)
        xc_data_canada = r.json()
        print("CANADA BIRD DATA: ")
        print(xc_data_canada['recordings'][0])
        print(xc_data_canada['recordings'][0]['url']) # is the actual url as str
        # bird_object = xc_data_canada['recordings'][0]['en']
        # print(bird_object) 


    # xc_params = {
    # 'query': 'cnt:brazil'
    # }

    # r = requests.get(url=xc_URL, params=xc_params)
    # xc_data = r.json()

    # print(xc_data)
    # print(type(xc_data))

    # name_en = xc_data['re.cordings'][0]['en']

    # for i in range(len(xc_data['recordings'])):
    #     print("XC DATA incremented index EN: ")
    #     print(xc_data['recordings'][i]['en'])

    # print(name_en)

    return render_template('text_xc.html')


@app.route('/birds/<species_code>')
def view_birds(species_code):
#     """Show details of a specific bird."""
    
    # Will sometimes get this error, assuming there aren't enough photo IDs to populate list
    # json.decoder.JSONDecodeError
    # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

    # user = None

    # if user == None:
    #     return render_template('user_oops.html')

    # user = User.query.get(session['user_id'])

    # user = User.query.get(session['user_id'])
    favorite = Favorite.query.all()

    print(species_code)

    ebird_URL = 'https://ebird.org/ws2.0/ref/taxonomy/ebird'

    ebird_params = {
        'fmt': 'json',
        'locale': 'en',
        'species': [species_code]
    }

    headers = {
    'X-eBirdApiToken': os.environ['ebird_api_key']
    }

    # https://ebird.org/ws2.0/ref/taxonomy/ebird?fmt=json&locale=en&species=coohaw&key=o42fhp5kl3t3

    r = requests.get(url = ebird_URL, params = ebird_params, headers = headers)
    bird_data = r.json()
    print("r")
    print(r)
    print("BIRD DATA")
    print(bird_data) #This is an ebird object with coohaw as the species name 
    print(type(bird_data)) # this is a list?????????

    if not bird_data:
        return render_template('bird_oops.html')

    bird_common_name = bird_data[0]['comName']
    bird_sci_name = bird_data[0]['sciName']
    bird_obj = get_ebird_info(species_code)
    bird_photo_id = get_photos_by_text(bird_common_name)
    bird_photo = get_image_flickr(bird_photo_id)
    # bird_photo is a list of the four photo URLs under the specified size

    # print("BIRD SCIENTIFIC NAME IS: ", bird_sci_name)
    # print("BIRD COMMON NAME IS: ", bird_common_name)

    # check_user_favorite

    # if user fave exists: 
        # add_user_favorite(bird_common_name, bird_sci_name)
  

    return render_template("bird_page.html", bird=bird_obj, bird_photo=bird_photo)


def get_ebird_info(species_code):
    """Gets common name and scientific name from eBird API"""

    ebird_URL = 'https://ebird.org/ws2.0/ref/taxonomy/ebird'

    ebird_params = {
        'fmt': 'json',
        'locale': 'en',
        'species': [species_code]
    }

    headers = {
    'X-eBirdApiToken': os.environ['ebird_api_key']
    }

    r = requests.get(url=ebird_URL, params=ebird_params, headers=headers)
    bird_data = r.json()
    
    if not bird_data: 
        return render_template('bird_oops.html')

    return bird_data[0]


def get_photos_by_text(text):
    """Returns photo objects using a comName keyword 'text' from eBird API"""
    """Gets photo object "ID" attribute from JSON file"""

    # make get request using common name of bird to get objects with that name
    # in the "title" attribute

    photo_by_title_URL = 'https://api.flickr.com/services/rest/'
    
    title_params = {
        'method': "flickr.photos.search",
        'api_key': os.environ['flickr_api_key'],
        'text': text,
        'format': 'json',
        'nojsoncallback': '1'
    }

    r = requests.get(url = photo_by_title_URL, params = title_params)
    photo_data = r.json()

    print("PHOTO DATA AND TYPE: ")
    print(photo_data)
    print(type(photo_data)) # dict
    # photo_id = photo_data['photos']['photo'][4]['id']

    photo_ids = []
  
    for i in range(0, 4):
        photo = photo_data['photos']['photo'][i]['id']
        photo_ids.append(photo)

    # photo_ids is a list of four photo IDs from the Flickr JSON file
    print("PHOTO IDS: ")
    print(photo_ids)
    return photo_ids


def get_image_flickr(photo_ids):
    """Get actual photo based on photo ID"""

    actual_image_URL = 'https://api.flickr.com/services/rest/'
    photo_urls = []

    # https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=5951cc9bf3af0c29009e5d4c3a1c249d&photo_id=43857180190&format=json&nojsoncallback=1&auth_token=72157672986552207-a3b472cc198424ff&api_sig=e5dc7aab0bf8f33e438232ed256d8f71
    # https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=0381854dcbbad40ac9a09a07365cbd6a&photo_id=43857180190&format=json&nojsoncallback=1&auth_token=72157672986552207-a3b472cc198424ff&api_sig=e5dc7aab0bf8f33e438232ed256d8f71

    # photo_ids is a list 
    for photo_id in photo_ids:
        
        params = { 'method': 'flickr.photos.getSizes',
        'api_key': os.environ['flickr_api_key'],
        'photo_id': photo_id,
        'format': 'json',
        'nojsoncallback': '1',
        }
        
        r = requests.get(url=actual_image_URL, params=params)
        photo_data = r.json()

        # Number index specifies desired size dimension 
        bird_src = photo_data['sizes']['size'][4]['source']

        photo_urls.append(bird_src)

    print("PHOTO URLS LIST: ")
    print(photo_urls)
    print("TYPE OF PHOTO URLS: ")
    print(type(photo_urls))
    # photo_urls is a list of four URLs that correspond to the IDs from get_photos_by_text
    return photo_urls

#     bird = Bird.query.get(bird_id) 
#     user = User.query.get(session['user_id'])
#     # print("THE USER IS: ")
#     # print(user)
#     # print(user.user_id)
#     # returns user object
#     # bird = Bird.query.get(bird_id) # bird by bird_id
#     # print("THE BIRD IS:")
#     # print(bird)

@app.route('/add_fave', methods=['POST'])
def add_user_favorite(common_name, sci_name):

    bird_common_name = request.forms.get('common_name')
    bird_sci_name = request.forms.get('sci_name')

    bird = Bird(common_name=bird_common_name, scientific_name=bird_sci_name)
    db.session.commit()

@app.route('/remove_fave', methods=['POST'])
def remove_user_favorite():



    db.session.delete(bird)

def check_user_favorite():
    """Checks if entry for a specific bird/user pair exists in the favorites table"""
    favorite = Favorite.query.all()

    # we need to know the user id and check if the common name exists, the bird ID is the comName
    if favorite:
        print("This bird is a user favorite.")
    else: 
        print("USER DOES NOT LIKE THIS BIRD. SHAME ON THEM.")

    pass
#     return render_template('bird_page.html', species=species_code)


# make fave route with post request
@app.route('/favorite/<bird_id>', methods=['POST']) 
def add_remove_favorite(bird_id):
    """Adds or removes bird from favorites table"""
    print(bird_id) # gives correct info - bird ID number
    print('we are going to favorite a bird with id {}'.format(bird_id))

    favorite = Favorite(bird_id=bird_id, user_id=session['user_id'])
    # favorite = Favorite.query.filter_by(bird_id=bird_id).get()
    check_favorite = Favorite.query.filter((Favorite.user_id == session['user_id']), (Favorite.bird_id == bird_id))
    # Check that user var matches an entry in db
    # user = User.query.filter(User.email == email).first()
    # favorite = Favorite.query.filter(Favorite.bird_id == bird.id).first()


    if check_favorite:
        db.session.delete(check_favorite)
        db.session.commit()

    else:
        db.session.add(favorite)
        db.session.commit()

    return "Success!"


@app.route('/map')
def show_map():

    key = os.environ['google_maps_api_key']
    return render_template('map.html', key=key)


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