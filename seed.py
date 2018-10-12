from sqlalchemy import func
from model import User
from model import Bird
from model import Favorite
from model import Checklist
from datetime import datetime

from model import connect_to_db, db
from server import app


def load_users():
    """Load users into database."""

    print("Users")

    User.query.delete()

    for row in open("seed_data/users_data.txt"):
        row = row.rstrip()

        fname, lname, username, email, password = row.split("|")

        user = User(fname = fname.strip(),
                    lname = lname.strip(),
                    username = username.strip(),
                    email = email.strip(),
                    password = password.strip())
        print(user)
        db.session.add(user)

    db.session.commit()

def load_birds():
    """Load birds into database."""

    print("Birds")

    Bird.query.delete()

    for row in open("seed_data/birds_data.txt"):
        row = row.rstrip()
        common_name, scientific_name, number = row.split("|")

        for each_word in row: 
            each_word = each_word.strip()

        bird = Bird(common_name = common_name.strip(),
                    scientific_name = scientific_name.strip(),
                    number = number.strip())

        db.session.add(bird)
        
    db.session.commit()


# def load_favorites():

#     print("Favorites")

#     Favorite.query.delete()
#     """Load favorites into database."""

#     # favorites[0] = user_id
#     # favorites[1] = username
#     # favorites[2] = bird_id
#     # favorites[3] = common_name
#     # favorites[4] = scientific_name

#     for row in open("seed_data/<>"):
#         row = row.rstrip()

#         favorite = Favorite(bird_id = bird_id,
#                     user_id = user_id)

#         db.session.add(favorite)
        
#     db.session.commit()

# def load_checklist():
#     """Load checklist records into database.""" 

#     print("Checklist")

#     for row in open("seed_data/checklist_data"):
#         row = row.rstrip()

#         favorite = Favorite(bird_id = bird_id,
#                     user_id = user_id)

#         db.session.add(favorite)
        
#     db.session.commit()

def following():
    """Load favorited pairs into database."""
    print("Following")

    # for each row 


if __name__ == "__main__":

    connect_to_db(app)

    db.create_all() # In case tables haven't been created, create them

    load_users()
    load_birds()
    # load_favorites()
    # load_checklist()