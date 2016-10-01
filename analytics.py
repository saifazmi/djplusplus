import urllib2
import json
import re
from os import listdir
from os.path import expanduser
from random import shuffle, randint
from pydub import AudioSegment, playback

AUTHORIZATION = "Bearer BQD_5-LP_zX8qYTv97k20Uq_wjDZ4e3DW2v7s4I6B3VNxQQLZm9UKmebMCh0Q_81a9HkZS20tSKrjOPQlpy5JlxsQuV7QG7SbDDgAaUNICHQPL_qmxFbF1whrBadO9Os3wbpxnTv-sqC"
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
    return send_request("search?type=track&limit=1&q=" + query)["tracks"]["items"][0]["id"]


def get_analytics(track_id):
    return send_request("audio-analysis/" + track_id)


def get_sections(query):
    track_id = get_track_id(query)
    analytics = get_analytics(track_id)
    sections = analytics["sections"]
    sections = map(lambda section: dict(start=int(1000*section["start"]), duration=int(1000*section["duration"])), sections)
    return sections


def do_file(f):
    sections = get_sections(f)
    # sections = [{'duration': 17090, 'start': 0}, {'duration': 21356, 'start': 17090}, {'duration': 54395, 'start': 38446}, {'duration': 7199, 'start': 92842}, {'duration': 68318, 'start': 100041}, {'duration': 11558, 'start': 168359}, {'duration': 46519, 'start': 179918}, {'duration': 61686, 'start': 226438}, {'duration': 8007, 'start': 288124}]
    print sections
    chosen = randint(0, len(sections) - 1)
    print sections[chosen]
    full_f = MUSIC_FOLDER + "/" + f
    song = AudioSegment.from_mp3(full_f)
    song = song[sections[chosen]["start"]:]
    song = song[0:sections[chosen]["duration"]]
    playback.play(song)


def read_music():
    global MUSIC_FOLDER
    files = listdir(MUSIC_FOLDER)
    shuffle(files)
    for f in files:
        if not re.match(".*\\.mp3", f):
            continue
        # f = "Eminem - Kings Never Die.mp3"
        print f
        do_file(f)
        return

if __name__ == '__main__':
    try:
        read_music()
    except KeyboardInterrupt:
        print "Stopping..."
