from dotenv import load_dotenv

load_dotenv()

import os
import json
import time
import spotipy
import lyricsgenius


# Creating spotifyOAuth object
spotifyOAuth = spotipy.SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_APP_REDIRECT_URI"),
    scope="user-read-currently-playing",
)

# Spotify
spot_token = spotifyOAuth.get_access_token()
spotifyObject = spotipy.Spotify(auth=spot_token["access_token"])

# Genius lyrics
genius_token = os.getenv("GENIUS_CLIENT_SECRET")
genius = lyricsgenius.Genius(genius_token)


# For threading
result = [False]
counter = 1
index = 0

while True:
    info = f"\n\n\nGetting currently playing song's information and lyrics.\n\nPressing `Ctrl + C` to stop"
    print(info)

    current_song = spotifyObject.currently_playing()
    current_song_type = current_song["currently_playing_type"]
    is_playing = current_song["is_playing"]

    if not is_playing:
        print(">>> No song is playing. Taking a nap for 30secs, then will check again...")
        time.sleep(30)
    else:
        # checking currently_playing_type for respected outputs
        if current_song_type == "track":
            # Needed information of the song
            artist = current_song["item"]["artists"][0]["name"]
            song = current_song["item"]["name"]
            album = current_song["item"]["album"]["name"]
            album_release = current_song["item"]["album"]["release_date"]
            song_duration = current_song["item"]["duration_ms"]
            song_progress = current_song["progress_ms"]
            is_explicit = current_song["item"]["explicit"]

            # Getting time left of the song
            time_ms = song_duration - song_progress
            time_sec = int((time_ms / 1000))

            # printing out the needed information fetched
            song_info = f">>> Song: {song} \n>>> Artist: {artist} \n>>> Album: {album} \n>>> Released: {album_release} \n>>> Is explicit?: {is_explicit}\n\n"
            print()
            print(song_info)

            # Getting song's lyrics
            genius_song = genius.search_song(title=song, artist=artist)
            lyrics = ""

            try:
                lyrics = genius_song.lyrics
                print(f"\n\n>>> {song}'s Lyrics \n\n{lyrics}")
            except Exception:
                print(f"\n\n >>> Cannot find song's lyrics.\n\nSleeping till next song")

            # sleeping till the end of the song + buffer
            time.sleep(time_sec + 1)

        # Checking if an add is playing (for the people without Spotify Premium)
        elif current_song_type == "ad":
            # If an add is playing, sleep till the ad is over

            print(f">>> Seems like an ad popped up --- sleeping till that is over!")
            time.sleep(30)

    # Check if access token has expired or not
    if spotifyOAuth.is_token_expired(spot_token) == True:

        print(
            ">>> Seems like the Spotify token has expired...\nHold onto your beat while a new one is fetched!"
        )

        token = spotifyOAuth.get_access_token()
        spotifyObject = spotipy.Spotify(auth=token["access_token"])
