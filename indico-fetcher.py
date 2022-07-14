#!/usr/bin/env python3

import requests
import urllib.request
import json
import os
import time
import dateutil.parser

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

def build_indico_request(path, params):
    items = list(params.items()) if hasattr(params, 'items') else list(params)
    if not items:
        return path
    return '%s?%s' % (path, urlencode(items))

def exec_request(indico_instance, request_path):
    req_headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    req = requests.get(indico_instance + request_path, headers=req_headers)
    return req

if __name__ == '__main__':
    INDICO_INSTANCE = 'https://indico.hiskp.uni-bonn.de'
    EVENT_ID = 3
    PATH = '/export/event/%d.json' % EVENT_ID
    PARAMS = {
        'limit': 500,
        'detail': 'contributions'
    }
    request_path = build_indico_request(PATH, PARAMS)
    req = exec_request(INDICO_INSTANCE, request_path)
    try:
      jresp = json.loads(req.content)
    except:
      print("Error parsing JSON response!")
      os.exit(1)

    for contrib in jresp['results'][0]['contributions']:
      if 'startDate' not in contrib:
        continue
      if contrib['startDate'] is None:
        continue

      date = contrib['startDate']['date']
      fulldir = date
      try:
        os.mkdir(fulldir)
      except FileExistsError:
        pass

      try:
        room = contrib['room'].split().pop(-1)
      except:
        room = contrib['room']

      if len(room) > 0:
        fulldir += "/" + room
      try:
        os.mkdir(fulldir)
      except FileExistsError:
        pass

      slot = contrib['startDate']['time'] + "_" + contrib['endDate']['time']
      fulldir += "/" + slot
      try:
        os.mkdir(fulldir)
      except FileExistsError:
        pass

      folders = contrib['folders']

      for folder in folders:
        for attachment in folder['attachments']:
          mod = attachment['modified_dt']
          mtime = dateutil.parser.parse(mod)
          mtimets = int(time.mktime(mtime.timetuple()))
          full_filename = fulldir + "/" + str(mtimets) + "_" + attachment['filename']

          if not os.path.isfile(full_filename):
            print('Downloading: ' + full_filename)
            try:
              urllib.request.urlretrieve(attachment['download_url'], full_filename)
            except Exception as exc:
              print(exc)
              print('  Encountered unknown error. Continuing.')

