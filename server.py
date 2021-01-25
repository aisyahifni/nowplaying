from flask import Flask, request, render_template, redirect, url_for, session
import json
import re
from twitter import Twitter
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import requests
import spotipy.util as util

app = Flask(__name__)
app.secret_key = '1234'
client_id = '9556eb2bb1524439ba0171dd57c869f5'
client_secret = 'ef6f71f5adea40a3a7cc757c8ca8e198'

# credentials=SpotifyClientCredentials(client_id, client_secret)
# token = util.prompt_for_user_token(username = "y12qqe9gp5wn5y5kdrh5rws43", scope="playlist-modify-private playlist-modify-public user-library-read", client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:5000/callback")
# spotify = spotipy.Spotify(auth=token)
# usertoken = ""
regex = re.compile(r"#nowplaying", re.IGNORECASE)

twitter = Twitter()

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        if request.form.get("username", "") != "":
            username = request.form.get("username")
            print("The username is", username)
            return redirect(url_for('search', username = username))
        elif request.form.get("userid", "") != "":
            # session['userid'] = request.form.get("userid")
            print("The userid is", request.form.get("userid"))
            print(spotify.me())
            session['userid'] = spotify.me()['id']
            # session['token'] = util.prompt_for_user_token(username = userid, scope="playlist-modify-private playlist-modify-public", client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:5000/callback")
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    if request.method == "POST":
        print(request.form.get("userid", ""))
        # token = util.prompt_for_user_token(username = request.form.get("userid", ""), scope="playlist-modify-private playlist-modify-public user-library-read", client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8000/callback")
        session['token'] = request.form.get("token", "")
        print(session['token'])
        # request.form.get("userid", "")
    return render_template('index.html')

@app.route('/callback')
def callback():
    print(request)
    return render_template('callback.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/api/search')
def search():
    hashtag = request.args.get('hashtag', '#nowplaying')
    username = request.args.get('username')
    tweets = twitter.search(hashtag, username)
    tracks = []
    
    spotify = spotipy.Spotify(auth=session['token'])

    for tweet in tweets:
        query = re.sub('#nowplaying', '', tweet.text, flags=re.IGNORECASE)
        results = spotify.search(q=query, type='track')
        tracks.append(results['tracks']['items'][0])

    return redirect(url_for('recs', artists = tracks[0]["artists"][0]["id"], tracks = tracks[0]["id"]))
    # return json.dumps(tracks)

@app.route('/recs')
def recs():
    artists = request.args.get('artists')
    tracks = request.args.get('tracks')
    spotify = spotipy.Spotify(auth=session['token'])
    recommendation_results = spotify.recommendations(seed_artists=[artists], seed_tracks=[tracks], limit=20, min_energy=0.2)
    userid = spotify.me()["id"]
    paras = '{\"name\": \"#nowplaying\",\"description\": \"New playlist description\",\"public\": false}'
    #response = requests.post(url=f"https://api.spotify.com/v1/users/{userid}/playlists", data=paras, headers={'Authorization': f'Bearer {token}'})
    response = spotify.user_playlist_create(user = userid, name = '#nowplaying', public = True, collaborative = False, description="")
    # print(response.json()["id"])
    # print(response.json())
    print(response)
    id = response["id"]
    results = spotify.playlist_add_items(id, [ track['uri'] for track in recommendation_results["tracks"]])
    return redirect(url_for('result', playlistid = id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)