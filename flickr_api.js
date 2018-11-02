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

    photo_ids = []
  
    for i in range(0, 4):

        photo = photo_data['photos']['photo'][i]['id']
        photo_ids.append(photo)

    return photo_ids


def get_image_flickr(photo_ids):
    """Get actual photo based on photo ID"""

    actual_image_URL = 'https://api.flickr.com/services/rest/'
    photo_urls = []

    for photo_id in photo_ids:
        
        params = { 'method': 'flickr.photos.getSizes',
        'api_key': os.environ['flickr_api_key'],
        'photo_id': photo_id,
        'format': 'json',
        'nojsoncallback': '1',
        }
        
        r = requests.get(url=actual_image_URL, params=params)
        photo_data = r.json()
        bird_src = photo_data['sizes']['size'][4]['source']
        photo_urls.append(bird_src)

    return photo_urls
