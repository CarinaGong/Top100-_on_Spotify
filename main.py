from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json


scope = "playlist-modify-public user-library-read"
client_ID = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
username = os.environ["SPOTIPY_USER"]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_ID,
                                               client_secret=client_secret,
                                               redirect_uri="http://example.com",
                                               scope=scope,
                                               username=username,
                                               ))

date = input("Which year would you like to travel back to? Type the date in this format YYYY-MM-DD: \n")
year = int(date[:4])

# scraping from Billboard of top 100 song of a certain date
response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
soup = BeautifulSoup(response.text, "html.parser")

top_100 = []
results = soup.find_all(class_="o-chart-results-list-row-container")
for result in results:
    song = result.find(name="h3", id="title-of-a-story")
    song_name = song.getText()
    song_n = song_name.strip("\n\t")
    holder = result.find(name="li", class_="lrv-u-width-100p")
    artist = holder.find(name="span")
    artist_name = artist.getText()
    artist_n = artist_name.strip("\n\t")
    diction = {
        "track": song_n,
        "artist": artist_n
    }
    top_100.append(diction)

# add top 100 songs into a separate file with a list of dictionaries
with open("billboard100.txt", "w") as file:
    js = json.dumps(top_100)
    file.write(js)
with open("billboard100.txt") as txt:
    js = json.loads(txt.read())


uri_list = []
# find track URI
for i in range(len(js)):
    track_ = js[i]["track"]
    # artist = js[i]["artist"]
    result = sp.search(q=f'track:{track_} year:{year}', type="track", limit=10, offset=0, market="US")
    try:
        uri_list.append(result["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{track_} doesn't exist in Spotify. Skipped.")
        pass

# create spotify playlist
create = sp.user_playlist_create(user=username, name=f"{date} Billboard 100", public=True,
                                 description="Musical Time Machine", collaborative=False)
playlist_id = create["id"]


# add tracks to the playlist
results = sp.playlist_add_items(playlist_id=playlist_id, items=uri_list, position=None)


