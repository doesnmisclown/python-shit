import uuid
import urllib.parse
from json import dumps
import requests
from bs4 import BeautifulSoup
next_batch = None
base_url = "https://matrix.org/_matrix/client/v3"
access_token = "токенсюда"
def onmessage(rid,event):
  if event.get("content").get("body") == "!анекдот":
    r = requests.get("https://baneks.site/random")
    soup = BeautifulSoup(r.text,"lxml")
    anek = soup.find(itemprop="description")
    payload = dumps(dict(body=anek.get_text("\n"),msgtype="m.text"))
    r2 = requests.put(f"{base_url}/rooms/{urllib.parse.quote(rid)}/send/m.room.message/{uuid.uuid4()}",headers={'Content-type':'application/json','Authorization':f'Bearer {access_token}'},data=payload)
while True:
  r = requests.get(f"{base_url}/sync",params=dict(since=next_batch,timeout=1000,access_token=access_token))
  json = r.json()
  next_batch = json.get("next_batch")
  if "rooms" in json:
    if "invite" in json.get("rooms"):
      for rid in json.get("rooms").get("invite").keys():
        r = requests.post(f"{base_url}/rooms/{rid}/join",params=dict(access_token=access_token))
    if "join" in json.get("rooms"):
      for rid, jroom in json.get("rooms").get("join").items():
        if "timeline" in jroom:
          for event in jroom.get("timeline").get("events"):
            content = event.get("content")
            if "body" in content:
              onmessage(rid,event)
            
