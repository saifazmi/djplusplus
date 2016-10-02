import urllib2
import re
from os import listdir
from os.path import expanduser
from random import shuffle, randint
from pydub import AudioSegment, playback, effects
from request import send_request
from tempfile import TemporaryFile
import sys

MUSIC_FOLDER = expanduser("~") + "/Music"
OUT_SONG = None
RIGGED = False
RIGGED_COUNT = 0

# Command line argument stuff.
i = 0
for arg in sys.argv:
    if i == 1:
        MUSIC_FOLDER = expanduser("~") + "/Music"  # arg # TODO
    elif i == 2:
        OUT_SONG = arg
    i += 1


def get_track_id(query):
    query = query[:-4]
    query = urllib2.quote(query)
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
    global RIGGED, RIGGED_COUNT
    sections = get_sections(analytics)
    if sections is None:
        return None
    print sections
    chosen = 0
    for i in range(0, 5):
        chosen = randint(1, len(sections) - 2)  # choose an index randomly to select a
        if sections[chosen]["duration"] > 5000:
            break

    if RIGGED:
        if RIGGED_COUNT == 0:
            RIGGED_COUNT = 1
            sections[chosen] = {'duration': 17203, 'start': 72681}
        else:
            sections[chosen] = {'duration': 28482, 'start': 186533}
    print sections[chosen]
    full_f = MUSIC_FOLDER + "/" + f
    song = AudioSegment.from_mp3(full_f)
    song = song[sections[chosen]["start"]:]
    song = song[0:sections[chosen]["duration"]]  # filter out the single section
    return song


def append(first, second, crossfade=100, overlap=800):
    seg1, seg2 = AudioSegment._sync(first, second)
    
    # match_target_amplitude(seg1, 0)
    # match_target_amplitude(seg2, 0)
    mid = int((seg1.rms + seg2.rms) / 2)
    seg1.apply_gain(mid - seg1.rms)
    seg2.apply_gain(mid - seg2.rms)

    if not crossfade:
        return seg1._spawn(seg1._data + seg2._data)

    frame_rate = int((seg1.frame_rate + seg2.frame_rate) / 2)
    
    xf = seg1[-crossfade:].set_frame_rate(frame_rate).fade_out(crossfade)
    xf *= seg2[:crossfade].set_frame_rate(frame_rate).fade_in(crossfade)
    
    output = TemporaryFile()

    output.write(seg1[:-crossfade]._data)
    output.write(xf._data)
    output.write(seg2[crossfade:]._data)

    output.seek(0)
    return seg1._spawn(data=output)


def read_music():
    global MUSIC_FOLDER, RIGGED
    files = listdir(MUSIC_FOLDER)  # gives a list of all the files in the music folder
    shuffle(files)  # shuffles the files within the list
    if RIGGED:
        files = ["Tristam - Frame of Mind.mp3", "Sia - Chandelier.mp3"]
        # files[1] = "Linkin Park - Waiting for the End.mp3"
    songs_by_key = {}
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
        # else:
        #     # Else is temporary, we just care about the first 2 songs matching.
        #     songs_by_key[str(key)].append(song)
        #     songs_by_key = {str(key): songs_by_key[str(key)]}
        #     break
        songs_by_key[str(key)].append(song)
    
    while True:
        key = songs_by_key.keys()[randint(0, len(songs_by_key.keys()) - 1)]
        
        print "Mixing " + str(len(songs_by_key[str(key)])) + "songs"
        out = None
        for song in songs_by_key[str(key)]:
            if out is None:
                out = song
            else:
                out = append(out, song, 7000)
        
        if OUT_SONG is None:
            playback.play(out)
        else:
            out.export(OUT_SONG)

if __name__ == '__main__':
    try:
        while True:
            read_music()
    except KeyboardInterrupt:
        print "Stopping..."
