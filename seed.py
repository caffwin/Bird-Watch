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

        db.session.add(user)

    db.session.commit()


def load_birds():
    """Load birds into database."""

    print("Birds")

    Bird.query.delete()

    for row in open("seed_data/birds_data.txt"):
        row = row.rstrip()
        scientific_name, common_name, species_code, image = row.split("|")

        bird = Bird(scientific_name = scientific_name.strip(),
                    common_name = common_name.strip(),
                    species_code = species_code,
                    image = image.strip())

        db.session.add(bird)
        
    db.session.commit()


def load_favorites():

    print("Favorites")

    Favorite.query.delete()
    """Load favorites into database."""

    for row in open("seed_data/favorites_data.txt"):
        row = row.rstrip()
        user_id, bird_id = row.split("|")

        favorite = Favorite(user_id = user_id.strip(),
                            bird_id = bird_id.strip())

        db.session.add(favorite)
        
    db.session.commit()


# def load_checklist():

#     print("Checklist")

#     Checklist.query.delete()
#     """Load favorites into database."""

#     for row in open("seed_data/checklist_data.txt"):
#         row = row.rstrip()
#         user_id, common_name, seen = row.split("|")

#         checklist = Checklist(user_id = user_id.strip(),
#                               common_name = common_name.strip(),
#                               seen = seen.strip())

#         db.session.add(checklist)
        
#     db.session.commit()


# def following():
#     """Load favorited pairs into database."""
#     print("Following")

#     # for each row 


if __name__ == "__main__":

    connect_to_db(app)

    db.create_all() # In case tables haven't been created, create them

    load_users()
    load_birds()
    load_favorites()
    # load_checklist()