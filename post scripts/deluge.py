#!/usr/bin/env python
# ======================================== #
# ============= INSTRUCTIONS ============= #

# Add file to Deluge's Execute plugin for event Torrent Complete

# Add api information to conf:

watcherapi = 'APIKEY'
watcheraddress = u'http://localhost:9090/'
category = 'Watcher'

#  DO NOT TOUCH ANYTHING BELOW THIS LINE!  #
# ======================================== #

import json
import os
import sys
import urllib
import urllib2

data = {}

args = sys.argv

download_dir = args[3]

while download_dir[-1] in ['/', '\\']:
    download_dir = download_dir[:-1]

parent_folder = os.path.split(download_dir)[-1]

if parent_folder.lower() != category.lower():
    # Not watcher category
    sys.exit(0)

data['apikey'] = watcherapi

data['name'] = args[2]
data['path'] = '{}/{}'.format(download_dir, args[2])
data['downloadid'] = args[1]
data['guid'] = args[1]
data['mode'] = 'complete'

url = u'{}/postprocessing/'.format(watcheraddress)
post_data = urllib.urlencode(data)

request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
response = json.loads(urllib2.urlopen(request, timeout=600).read())

if response['status'] == 'finished':
    sys.exit(0)
elif response['status'] == 'incomplete':
    sys.exit(1)
else:
    sys.exit(1)

sys.exit(0)

# pylama:ignore=E402
