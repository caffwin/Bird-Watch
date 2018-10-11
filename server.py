from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import Bird, User, Favorite, Checklist, connect_to_db, db

app = Flask(__name__)

app.secret_key = "secret_key"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage"""
    if 'user_id' in session:
        # logged_name = User.query.filter_by(user_id == session['user_id']) Find username that matches
        # ID of user logged in
        print('You are logged in as ' + str(session['user_id']))
    else:
        print('No one is currently logged in.')

    return render_template('homepage.html')

# @app.route('/login', methods=['POST'])
# def login_form():

@app.route('/login', methods=['GET'])
def login_form():

    return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login_process():
    # Users may use email OR username to log in
    login_id = request.form.get('login_id')
    password = request.form.get('password')

    user = User.query.filter(User.email == login_id).first()

    if not user:
        user = User.query.filter(User.username == login_id).first()


    if user:
        if user.password == password:
            print("Password matches username!")
            flash("Logged in")
            session['user_id'] = user.user_id # saves to session
            # allows us to show user on any page
            return redirect('/users/{}'.format(user.user_id))

        else: 
            print("Password does not match user!")
            flash("Incorrect Password")

    else: 
        print("User not found! Please try again, or register.")
        return redirect('/')

@app.route('/register', methods=['GET'])
def registration_form():

    return render_template('register_page.html')

@app.route('/register', methods=['POST'])
def registration_process():

    username = request.form.get('reg_username')
    email = request.form.get('reg_email')
    password = request.form.get('reg_pw')

    # Check that user var matches an entry in db
    user = User.query.filter(User.email == email).first()

    if user == None: # If user doesn't exist in db
        # Add user to db
        print("User added!")
        flash("User added!")
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

    else:
        print("This user already exists! Please log in.")
        flash("This user already exists! Please log in.")

    # return redirect('/users/{}'.format(user.user_id))
    return redirect('/')
    # Redirect to home page


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("users_list.html", users=users)


@app.route('/user/<user_id>')
def user_profile(user_id):

    user = User.query.get(user_id)

    return render_template('user_profile.html', user=user)



if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')