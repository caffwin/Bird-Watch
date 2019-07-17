Bird Watch is a full stack Flask web application that allows the user to create a bird-watching list. Users may search from thousands of species anywhere in the world through eBird's API that produces dynamically generated personalized pages for each bird with photos from the Flickr API and song clips from Xeno-Canto's API. 

The “Map” page uses the Google Maps Geolocate API to request the user's coordinates and returns markers of nearby bird species on the map that populates a dropdown menu. Select a bird’s name from this menu to go to its dynamically generated page, containing details about the bird. Users may add or remove this bird as a favourite on the bird’s page as well as on their personal page, where additional settings may be modified. Users may also view and edit their full bird-watching list on their personal pages.


MacOS installation instructions for Bird Watch:

1) Install requirements: 
pip install -r requirements.txt

2) Create and configure postgreSQL database: 
createdb mydb 
psql mydb

3) Run server: 
python3 server.py



Front end: HTML5, CSS3, Jinja2, Jaascript, jQuery, Bootstrap
Back end: Python, Flask, PostgreSQL, SQLAlchemy
APIs: Google Maps, eBird, Flickr, Xeno-Canto

Deployed with AWS Lightsail upon completion.

