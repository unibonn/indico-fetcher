#!/usr/bin/env python3

# SPDX-License-Identifier: MIT

import json
import os
import re
import sys
import time
import urllib.request
import requests
import dateutil.parser
import yaml

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
    if AUTH_TOKEN is not None:
        req_headers['Authorization'] = 'Bearer ' + AUTH_TOKEN
    req = requests.get(indico_instance + request_path, headers=req_headers)
    return req

if __name__ == '__main__':
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    INDICO_INSTANCE = config['indico_instance']
    EVENT_ID = config['event_id']
    PATH = '/export/event/%d.json' % EVENT_ID
    DISPLAY_SECS_IN_TIME_SLOT = config['display_secs_in_time_slot']
    LIMIT_FILE_SIZE = None
    if 'limit_file_size' in config:
        LIMIT_FILE_SIZE = config['limit_file_size']
    AUTH_TOKEN = None
    if 'auth_token' in config:
        AUTH_TOKEN = config['auth_token']
    PARAMS = {
        'limit': config['limit'],
        'detail': 'contributions'
    }

    request_path = build_indico_request(PATH, PARAMS)
    req = exec_request(INDICO_INSTANCE, request_path)
    try:
        jresp = json.loads(req.content)
    except:
        print("Error parsing JSON response!")
        sys.exit(1)

    if not jresp['results']:
        print("Error: Zero contributions found! This might be caused by lack of permissions.")
        sys.exit(1)

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

        if DISPLAY_SECS_IN_TIME_SLOT is True:
            slot = contrib['startDate']['time'] + "_" + contrib['endDate']['time']
        else:
            slot = contrib['startDate']['time'][:-3] + "_" + contrib['endDate']['time'][:-3]
        # Some OSs and FSs don't like colons:
        slot = slot.replace(':', '.')
        fulldir += "/" + slot
        try:
            os.mkdir(fulldir)
        except FileExistsError:
            pass

        folders = contrib['folders']

        SERVER_REPORTS_FILESIZE = True

        if AUTH_TOKEN is not None:
            download_opener = urllib.request.build_opener()
            download_opener.addheaders = [('Authorization', 'Bearer '+AUTH_TOKEN)]
            urllib.request.install_opener(download_opener)

        for folder in folders:
            for attachment in folder['attachments']:
                mod = attachment['modified_dt']
                mtime = dateutil.parser.parse(mod)
                mtimets = int(time.mktime(mtime.timetuple()))
                if attachment['type'] != 'file':
                    print(f"Skipping non-file attachment (type: {attachment['type']})...")
                    continue
                # Remove any bad characters from filenames:
                sanitized_filename = re.sub('[^\w\.\s-]', '', attachment['filename'])
                full_filename = fulldir + "/" + str(mtimets) + "_" + sanitized_filename

                if not os.path.isfile(full_filename):
                    print('Downloading: ' + full_filename)
                    try:
                        download_url = attachment['download_url']
                        if (LIMIT_FILE_SIZE is not None) and SERVER_REPORTS_FILESIZE:
                            file_meta = urllib.request.urlopen(download_url).info()
                            if file_meta.get_all("Content-Length") is None:
                                # Can happen if server uses chunked encoding, for example.
                                SERVER_REPORTS_FILESIZE = False
                                print("Can not check file sizes, server does not report size in advance, ignoring limit!")
                            else:
                                file_size = int(file_meta.get_all("Content-Length")[0])
                                if file_size > LIMIT_FILE_SIZE:
                                    print(f"File size of {full_filename} is beyond configured limit. Ignoring this file.")
                                    continue
                        urllib.request.urlretrieve(download_url, full_filename)
                    except Exception as exc:
                        print(exc)
                        print('  Encountered unknown error. Continuing.')
