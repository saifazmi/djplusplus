import json
import urllib2
import os.path
import base64

AUTHORIZATION = "Bearer BQBfy8hAprSm4ccYKQnN9XyQQwXwForU9Fa-Qh647FW8V4-gUNCztIsVcRW7O_kwglxI1baUEz7wtVZNkR9EcVzTR_oddU7FqySmKL1Wt88iuKb7bQhsin5BrlkjZkO9nspbU6Egmaub"


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
