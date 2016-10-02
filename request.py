import json
import urllib2
import os.path
import base64

AUTHORIZATION = "Bearer BQD0RgVM-tfajxQwsGaHsfWH5Hs8E7k0064iLbYTuQcQLR1EWybwZMlYUY2Ov9dFU9p6rhc5Ik15_zApKub5HL1q8TpvTieuV1Dv-Hkz2ldUGM0oCG0xNE-x3eFPBuApnPcCoj2TKCxY"


def send_request(end_path):
    global AUTHORIZATION
    cached = check_cache(end_path)
    if cached is not None:
        return cached
    req = urllib2.Request("https://api.spotify.com/v1/" + end_path)
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", AUTHORIZATION)
    resp = urllib2.urlopen(req)
    content = resp.read()
    update_cache(end_path, content)
    return json.loads(content)


def check_cache(url):
    url = base64.b64encode(url).replace("/", "_")
    if not os.path.isfile("cache/" + url):
        return None
    f = open("cache/" + url, "r")
    son = json.loads(f.read())
    f.close()
    return son


def update_cache(url, item):
    url = base64.b64encode(url).replace("/", "_")
    f = open("cache/" + url, "w")
    f.write(item)
    f.close()
