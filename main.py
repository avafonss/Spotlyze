from dotenv import load_dotenv
import os
import base64
from requests import post
from requests import get
import json

load_dotenv()

# get client id and client secret
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# take client id, concatenate to client secret,
# encode using base 64 encoding to retrieve 
# authorization token
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
    "Authorization": "Basic " + auth_base64,
    "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"

    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"  # fixed URL
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = result.json()
    return json_result["tracks"]

def get_detailed_tracks_for_artist(token, artist_id):
    """Get detailed track information including release dates and popularity for visualization"""
    # First get top tracks
    top_tracks = get_songs_by_artist(token, artist_id)
    
    # Get detailed track info including release dates
    detailed_tracks = []
    headers = get_auth_header(token)
    
    for track in top_tracks:
        # Get track details including popularity
        track_id = track['id']
        track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        track_result = get(track_url, headers=headers)
        
        if track_result.status_code == 200:
            track_data = track_result.json()
            
            # Get album details for release date
            album_id = track_data['album']['id']
            album_url = f"https://api.spotify.com/v1/albums/{album_id}"
            album_result = get(album_url, headers=headers)
            
            if album_result.status_code == 200:
                album_data = album_result.json()
                
                detailed_track = {
                    'name': track_data['name'],
                    'popularity': track_data['popularity'],
                    'release_date': album_data['release_date'],
                    'album_name': album_data['name'],
                    'duration_ms': track_data['duration_ms'],
                    'track_number': track_data['track_number']
                }
                detailed_tracks.append(detailed_track)
    
    return detailed_tracks



