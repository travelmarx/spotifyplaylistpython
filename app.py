# from crypt import methods
import os, sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, Response, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from requests import RequestException

app = Flask(__name__, static_folder='static')
CORS(app)
csrf = CSRFProtect(app)

# If these environment variables aren't set, can't run
if 'SPOTIPY_CLIENT_ID' in os.environ:
    SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
    SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']
    DEFAULT_PLAYLIST=os.environ['DEFAULT_PLAYLIST']
    print("Loading environment variables...")
else:
    sys.exit("Exiting...no environment variables specified.")

print("SPOTIFY_CLIENT_ID = " + SPOTIPY_CLIENT_ID)
print("SPOTIFY_CLIENT_SECRET = " + SPOTIPY_CLIENT_SECRET)

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# WEBSITE_HOSTNAME exists only in production environment
if not 'WEBSITE_HOSTNAME' in os.environ:
   # local development, where we'll use environment variables
   print("Loading config.development.")
   app.config.from_object('project.development')
else:
   # production
   print("Loading config.production.")
   app.config.from_object('project.production')

@app.route("/", methods=['GET', 'POST'])
@csrf.exempt
def index():

    # Todo: currently return items are capped at 100 

    if request.method == 'GET':
        playlist_id = DEFAULT_PLAYLIST
    else:
        playlist_id = request.form.get('id')

    track_list = []
    image_url_list = []
    playlist = sp.playlist(playlist_id=playlist_id, fields="images,description,owner,name,tracks.items(track(name), track(artists(name)), track(album(images)))")
    title = playlist['name']
    for idx, item in enumerate(playlist['tracks']['items']):
        #print(idx, item)
        # Todo: Really should iterate through artists if there are more than one. Currently, just get first '0'.
        track_list.append(item['track']['name'] + " - " + item['track']['artists'][0]['name'])
        image_url_list.append(item['track']['album']['images'][1]['url'])

    # We are relying on at least one image, hence index 0. But what if no images?
    playlist_image = playlist['images'][0]['url']
    playlist_desc = playlist['description']
    playlist_owner = playlist['owner']['display_name']

    return render_template('index.html', id=playlist_id, title=title, 
        tracks=track_list, image_urls=image_url_list, playlist_image=playlist_image, 
        description=playlist_desc, owner=playlist_owner)

@app.route('/get-csv/', defaults={'playlist_id': DEFAULT_PLAYLIST})
@app.route("/get-csv/<string:playlist_id>")
def get_csv(playlist_id):

    track_list = []
    playlist = sp.playlist(playlist_id=playlist_id, fields="name,tracks.items(track(name), track(artists(name)))")
    for idx, item in enumerate(playlist['tracks']['items']):
        track_list.append(item['track']['name'] + "," + item['track']['artists'][0]['name'] + "\r\n")

    generator = (cell for row in track_list
                    for cell in row)

    return Response(generator,
                       mimetype="text/csv",
                       headers={"Content-Disposition":
                                    "attachment;filename=playlist.csv"})

@app.route('/get-tracks/', defaults={'playlist_id': DEFAULT_PLAYLIST})
@app.route('/get-tracks/<string:playlist_id>')
def get_tracks(playlist_id):

    # create a dictionary instead of a list
    track_list = {}
    playlist = sp.playlist(playlist_id=playlist_id, fields="name,tracks.items(track(name), track(artists(name)), track(album(images)))")
    for idx, item in enumerate(playlist['tracks']['items']):
        track_list[idx] = {"name": str(item['track']['name']), "artist": str(item['track']['artists'][0]['name']), "thumb" : str(item['track']['album']['images'][1]['url'])}

    response = jsonify(track_list)

    return response
