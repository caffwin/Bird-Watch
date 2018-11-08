from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)
from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
from random import randint
from model import Bird, User, Favorite, Checklist, connect_to_db, db

from sqlalchemy import update # Might not need this

import requests 
import re
import os
import time
import json
import bcrypt


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

    user = None

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        print('You are logged in as ' + str(session['user_id']))
        flash('You are now logged in!')
        # print(user.fname)

    else:
        print('No one is currently logged in.')


    return render_template('homepage.html', user=user)


def get_hashed_password(plain_text_password):
    """Takes in a plain text password and returns the hashed/salted password"""
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    """Takes in plain text password & hashed password and compares them
    True if match, False if no match"""
    return bcrypt.checkpw(plain_text_password, hashed_password)


@app.route('/login')
def login_form():

    return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login_process():
    """Login Process"""

    username = request.form.get('login_id') #jhacks
    password = request.form.get('password') #jhacks

    user = User.query.filter(User.email == username).first()

    if not user:
        user = User.query.filter(User.username == username).first()
        print("User doesn't exist")
    
    if user:
        if len(password) > 8 & len(password) < 17: 
            check_pw = check_password(password, user.password)
            # if password = hashed_password
            if check_pw:
            # if user.password == password:
                print("Password matches username!")
                flash("You are now logged in!")
                session['user_id'] = user.user_id # saves to session
                # return redirect('/users/{}'.format(user.user_id))
                return redirect('/users/my_page')
                # Redirect here instead for personal feed
            # elif user.password == None:
            #     return redirect('/')

        else: 
            print("Please enter a password between 8-16 characters!")
            return redirect('/')
            # This happens when username typed, password blank

    else: 
        print("User not found! Please try again, or register.")
        return redirect('/')


@app.route('/register', methods=['GET'])
def registration_form():

    return render_template('register_page.html')

@app.route('/register', methods=['POST'])
def registration_process():

    username = request.form.get('reg-username')
    email = request.form.get('reg-email')
    password = request.form.get('reg-pw')
    hashed_pw = get_hashed_password(password)
    regex_email = re.findall(r'[^@]+@[^@]+\.[^@]+', email)
    #doesn't handle the case of spaces

    # check to make sure user doesn't already exist before
    # allowing new entry to be made in DB

    regex_username = re.match("^[a-zA-Z0-9_.-]+$", username)
    # must be alphanumeric
    # Returns none if strange characters entered or space in name
    # Returns match object if matching string 

    # if regex_username == None: # if it's something

    # if len(password) > 8 & len(password) < 17:
    #     valid_password = password

    fname = request.form.get('reg-fname')
    lname = request.form.get('reg-lname')

    # Check that user var matches an entry in db
    user = User.query.filter(User.email == email).first()

    if user == None: # If user doesn't exist in db
        # if regex_email: # if regex_username is valid
        # Add user to db
        print("User added!")
        flash("User added!")
        print(regex_username) # evaluated to none when "sdfosdijf  e9" entered
        if regex_username is not None:
            print("REGEX USERNAME: ")
            print(regex_username)
            print("Username alphanumeric!")
            flash("Username alphanumeric!")
        # make sure password also valid
        # if username.isalnum() == True:
            print("REGEX EMAIL: ")
            print(regex_email)
            if regex_email is not None: 
                print("Regex'd email is valid!")
        # user = User(username=username, password=hashed_pw, email=email, fname=fname, lname=lname)
                user = User(username=username, password=hashed_pw, email=email, fname=fname, lname=lname)
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.user_id

        else:
            print("One or more fields are invalid! Please try again.")
            return redirect('/register')
    else: # user already exists in db
        print("This user already exists! Please log in.")
        flash("This user already exists! Please log in.")

    flash("You are now registered! Please enjoy all of our features.")
    return redirect('/')
    

@app.route('/logout')
def logout_process():
    """Logs user out from website"""
    del session['user_id']
    return redirect('/')


@app.route('/users/my_page')
def user_feed():
    """Shows user's page (private), only viewable if logged in as user"""

    if 'user_id' not in session:
        flash("No user is logged in!")
        return render_template('user_oops.html')

    user = User.query.get(session['user_id'])

    if user: 
        if user.image_name:
            user.image_name = str(user.image_name) + '?{}'.format( str(time.time()) )

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
    
    params = {'lat': lat,
    'lng': lng 
    }

    headers = {
    'X-eBirdApiToken': key
    }

    URL = 'https://ebird.org/ws2.0/data/obs/geo/recent/'
    r = requests.get(url = URL, params = params, headers = headers)
    data = r.json()

    return jsonify(data)


@app.route('/upload', methods=['POST'])
def upload_file():
    user = User.query.get(session['user_id'])
    # check if the post request has the file part

    file = request.files['upload-image']
    image_name = None

    if 'upload-image' not in request.files: 
        flash("No file was selected - please choose one and resubmit.")
        return redirect('/users/my_page')

    if file.filename == '':
        # Fix this 
        flash("Oh no! Could not save image.")
        return redirect('/users/my_page')
    
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']) + '_profile.jpg'))

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
    new_username = request.form.get('upd-username')
    new_fname = request.form.get('upd-fname')
    new_lname = request.form.get('upd-lname')
    new_email = request.form.get('upd-email')
    new_pw = request.form.get('upd-pw')
    input_pw = request.form.get('check-pw')
    user = User.query.get(session['user_id'])
    print("Printing user: ")
    print(user)
    # check_pw = check_password(input_pw, user.password)



    # if new_fname.strip().isalpha():  #if new_fname is True (all characters):
    #     # new_fname.strip()
    #     new_fname.lower()
    #     new_fname.title()
    #     user.fname = new_fname

    # else: 
    #     print("Please enter a valid first name!")

    # if new_lname.strip().isalpha():
    #     # new_lname.strip()
    #     new_lname.lower()
    #     new_lname.title()
    #     user.lname = new_fname
    # else: 
    #     print("Please enter a valid last name!")

    # if new_username:
    #     # new_username.strip()
    #     user.username = new_username

    # else: 
    #     print("Please enter a valid first name!")

    # if new_email:
    #     new_email.strip()
    #     new_email.lower()
    #     user.email = new_email

    # strip if no trailing white space
    # entire username alphanumeric (letters & nums)
    # make sure user can't submit empty form
    # validate that data exists
    # if changing username, change & log out


    # ask for old pw too, if correct and
    # if check_pw == user.password: 
        # if new_pw == new_pw2: 
        #     new_hashed_pw = get_hashed_password(new_pw)
        #     user.password = new_hashed_pw
        #     db.session.commit()

        # else: 
        #     print("The passwords don't match! Try again")


    # print("USER'S OLD FIRST NAME IS: ")
    # print(user.fname)
    # print("USER'S FIRST NAME IS: ")
    # print(new_fname)

    # user.email = new_email
    # user.fname = new_fname
    # user.lname = new_lname
    # new_hashed_pw = get_hashed_password(new_pw)
    user.fname = new_fname
    user.lname = new_lname
    user.username = new_username
    user.email = new_email

    
    # user.username = new_username
    print("USER'S NEW FNAME IS: ")
    print(user.username)

    db.session.commit()

    return redirect('/users/my_page')

@app.route('/update_user_desc', methods=['POST'])
def update_user_desc():

    user_desc = request.form.get('profile-desc')
    user = User.query.get(session['user_id']) 

    if user_desc is not None:
        flash("Description updated!")
        user.description = user_desc
        db.session.commit()
        return redirect('/users/my_page')
    else:
        return redirect('/users/my_page')



@app.route('/get_bird_page_data')
def get_bird_code_and_name():
    """Gets data of species_code and common name from map.html template"""

    species_code = request.args.get('speciesCode')
    return redirect('/birds/' + species_code)


def get_xenocanto_json(comName):
    """Takes in a common name, and returns json of all sound clips.
    Returns either the link of an available sound clip, or None"""

    xc_URL = 'https://www.xeno-canto.org/api/2/recordings'

    xc_params = {
    'query': comName
    }

    r = requests.get(url=xc_URL, params=xc_params)
    xc_data = r.json()

    if len(xc_data['recordings']) > 0:
        print("length of recordings is more than zero")
        xc_soundclip = xc_data['recordings'][0]['url'] #may be out of range       
        print("XC SOUNDCLIP: ")
        print(xc_soundclip) 
        print("XC SOUNDCLIP LENGTH: ")
        print(len(xc_soundclip))
        print("XC SOUNDCLIP TYPE: ")
        print(type(xc_soundclip)) # string
        return xc_soundclip

    else: 
        print("Else statement entered")
        return None


def get_bird_data(species_code):
    """Gets data of a specific bird through eBird's API with a given species code"""

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

    return bird_data #bird_data is a single bird obj


@app.route('/birds/<species_code>')
def view_birds(species_code):
    """Show details of a specific bird."""

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
    print("BIRD DATA")
    print(bird_data) 
    print("BIRD DATA TYPE: ")
    print(type(bird_data)) 

    if not bird_data:
        return render_template('bird_oops.html')

    bird_common_name = bird_data[0]['comName']
    bird_sci_name = bird_data[0]['sciName']
    bird_obj = get_ebird_info(species_code)
    bird_photo_id = get_photos_by_text(bird_common_name)
    bird_photo = get_image_flickr(bird_photo_id)
    # bird_photo is a list of the four photo URLs under the specified size
    print("BIRD COMMON NAME IS: ")
    print(bird_common_name)
    print(type(bird_common_name))
    birds_in_db = Bird.query.all() 
    bird_obj_comname = bird_obj['comName'] 

    bird = Bird.query.filter(Bird.common_name == bird_obj_comname).first()

    favorite = None

    if bird:
        favorite = Favorite.query.filter(Favorite.user_id==session['user_id'], Favorite.bird_id==bird.bird_id).first() # find first entry with this

    xc_url = get_xenocanto_json(bird_common_name)
    
    print("XC URL IS: ")
    print(xc_url)

    flash("Navigated to bird page!")
    # potential error: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

    return render_template("bird_page.html", bird=bird_obj, bird_photo=bird_photo, favorite=favorite, xc_url=xc_url)


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

    # print("PHOTO DATA AND TYPE: ")
    # print(photo_data)
    # print(type(photo_data)) # dict
    # photo_id = photo_data['photos']['photo'][4]['id']

    photo_ids = []
  
    for i in range(0, 4):
        photo = photo_data['photos']['photo'][i]['id']
        photo_ids.append(photo)

    # photo_ids is a list of four photo IDs from the Flickr JSON file
    return photo_ids

def get_bird_pic_flickr(photo_id):
    """Gets one actual photo from flickr's API based on photo ID,
    this is the actual image!"""

    actual_image_URL = 'https://api.flickr.com/services/rest/'
    photo_url = []
    
    params = { 'method': 'flickr.photos.getSizes',
    'api_key': os.environ['flickr_api_key'],
    'photo_id': photo_id,
    'format': 'json',
    'nojsoncallback': '1',
    }
    
    r = requests.get(url=actual_image_URL, params=params)
    photo_data = r.json()

    # Number index specifies desired size dimension 
    bird_src = photo_data['sizes']['size'][3]['source']
    # bird_src is a list of one item - must be a list 
    photo_url.append(bird_src)

    return photo_url


def get_image_flickr(photo_ids):
    """Get four photos based on photo ID"""

    actual_image_URL = 'https://api.flickr.com/services/rest/'
    photo_urls = []

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

    # photo_urls is a list of four URLs that correspond to the IDs from get_photos_by_text
    return photo_urls


@app.route('/add_fave', methods=['POST'])
def add_user_favorite():
    """Adds bird to database if not already in database,
    Adds species code/user id pair to favorites if not already in database """

    common_name = request.form.get('comName')
    scientific_name = request.form.get('sciName')
    species_code = request.form.get('speciesCode')
    # get bird by matching common name, could also match species code
    bird = Bird.query.filter(Bird.common_name == common_name).first()
    user_id = session['user_id']
    user = User.query.get(session['user_id']) 

    photo_id = get_photos_by_text(common_name) # this is a photo ID
    image_url = get_bird_pic_flickr(photo_id)
    image_index = image_url[0]
    print("PHOTO ID IS: ")
    print(photo_id)
    print("IMAGE URLS IS: ")
    print(image_url)
    print(type(image_url))

    if not bird:
        print("Bird does not exist in db!")
        bird = Bird(common_name=common_name, scientific_name=scientific_name, species_code=species_code, image=image_index)
        db.session.add(bird)
        db.session.commit()
        print("Bird added, yay!")

    favorite = Favorite(user_id=session['user_id'], bird_id=bird.bird_id)

    db.session.add(favorite)
    db.session.commit()

    flash("Yay, added!")
    return redirect('/birds/' + species_code)


@app.route('/remove_fave', methods=['POST'])
def remove_user_favorite():
    # print("speciesCodes are: " + str(request.form.get('speciesCodes')))

    species_code = request.form.get('speciesCode')

    remove_favorite(species_code)
    # bird = Bird.query.filter(Bird.species_code == species_code).first()

    # check_favorite = Favorite.query.filter((Favorite.user_id == session['user_id']), (Favorite.bird_id == bird.bird_id)).first()

    # db.session.delete(check_favorite)
    # db.session.commit()
    print("Removed fave!")
    # return "Removed fave!"
    return redirect('/birds/' + species_code)


def remove_favorite(species_code):

    bird = Bird.query.filter(Bird.species_code == species_code).first()
    check_favorite = Favorite.query.filter((Favorite.user_id == session['user_id']), (Favorite.bird_id == bird.bird_id)).first()

    db.session.delete(check_favorite)
    db.session.commit()
    return "Removed!"


@app.route('/remove_faves', methods=['POST'])
def remove_numerous_faves():
    species_codes = request.form.get('speciesCodes')
    species_codes = json.loads(species_codes)

    for code in species_codes:
        remove_favorite(code)
        print("removed" + code)

    print("here are the species codes: ")
    print(species_codes)
    # return redirect('/users/my_page')
    return "Removed!"


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


@app.route('/get_user_id')
def get_user_info():
    """Takes in a username and returns a user id"""
    search_for_username = request.args.get('searchFor')
    print("Search for username is: ")
    print(search_for_username)
    user = User.query.filter(User.username == search_for_username).first()
    print("USER is: ")
    print(user)
    if user: 
        username_id = user.user_id
        print("User exists!")
        return render_template('user_profile.html')
    else: 
        print("There is no user!")
        return redirect('/users_list')


@app.route('/about')
def get_about_page():
    """About Page"""
    return render_template('about.html')

if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')