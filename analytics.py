import urllib2
import json
import re
from os import listdir
from os.path import expanduser
from random import shuffle, randint
from pydub import AudioSegment, playback

AUTHORIZATION = "Bearer BQAQbYWzeyAqhYoSDCAOS8o2F3k-2dHHB5zEL7G5EYkEXD2033cEU00a96A-XHecd9cX8WPL8s1CcY1rB_XCqDdPGC8WJmgNf3v2Ja5q1MvfM3NvuKo-qviIZQwqlCmacs1BuzFJxxzX"
MUSIC_FOLDER = expanduser("~") + "/Music"


def send_request(end_path):
    global AUTHORIZATION
    req = urllib2.Request("https://api.spotify.com/v1/" + end_path)
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", AUTHORIZATION)
    resp = urllib2.urlopen(req)
    content = resp.read()
    return json.loads(content)


def get_track_id(query):
    query = query.replace(" ", "+")[:-4]
    print query
    items = send_request("search?type=track&limit=1&q=" + query)["tracks"]["items"]
    if len(items) == 0:
        print "No Spotify data for this."
        return None
    return items[0]["id"]


def get_analytics(track_id):
    return send_request("audio-analysis/" + track_id)


def get_key(analytics):
    key = analytics["track"]["key"]
    return key


def get_sections(analytics):
    # returns all of the sections of the song from the spotify api
    sections = analytics["sections"]
    sections = map(lambda section: dict(start=int(1000*section["start"]), duration=int(1000*section["duration"])), sections) # pls explain
    return sections


def do_file(f, analytics):
    sections = get_sections(analytics)
    if sections is None:
        return None
    # sections = [{'duration': 17090, 'start': 0}, {'duration': 21356, 'start': 17090}, {'duration': 54395, 'start': 38446}, {'duration': 7199, 'start': 92842}, {'duration': 68318, 'start': 100041}, {'duration': 11558, 'start': 168359}, {'duration': 46519, 'start': 179918}, {'duration': 61686, 'start': 226438}, {'duration': 8007, 'start': 288124}]
    print sections
    chosen = randint(0, len(sections) - 1)  # choose an index randomly to select a
    print sections[chosen]
    full_f = MUSIC_FOLDER + "/" + f
    song = AudioSegment.from_mp3(full_f)
    song = song[sections[chosen]["start"]:]
    song = song[0:sections[chosen]["duration"]] # filter out the single section
    return song


def read_music():
    global MUSIC_FOLDER
    files = listdir(MUSIC_FOLDER)  # gives a list of all the files in the music folder
    shuffle(files)  # shuffles the files within the list
    songs_by_key = {}
    i = 0
    for f in files:
        if not re.match(".*\\.mp3", f):
            continue
        # f = "Eminem - Kings Never Die.mp3"
        print f
        track_id = get_track_id(f)
        if track_id is None:
            continue
        analytics = get_analytics(track_id)
        key = get_key(analytics)
        song = do_file(f, analytics)
        if str(key) not in songs_by_key.keys():
            songs_by_key[str(key)] = []
            print songs_by_key[str(key)]
        songs_by_key[str(key)].append(song)
        
        i += 1
        if i == 10:
            break
    
    key = 0
    while True:
        key = randint(0, len(songs_by_key) - 1)
        if str(key) in songs_by_key.keys():
            break
    
    out = None
    for song in songs_by_key[str(key)]:
        if out is None:
            out = song
        else:
            out *= song
    playback.play(out)


if __name__ == '__main__':
    try:
        read_music()
    except KeyboardInterrupt:
        print "Stopping..."
