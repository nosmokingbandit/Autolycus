from core import ajax, sqldb
import json
import logging
from core.helpers import Url
import time
import xml.etree.cElementTree as ET

logging = logging.getLogger(__name__)


class NewAlbums(object):
    def __init__(self):
        self.sql = sqldb.SQL()
        self.ajax = ajax.Ajax()
        self.rss = 'https://itunes.apple.com/WebObjects/MZStore.woa/wpa/MRSS/newreleases/sf=143441/limit=100/explicit=true/rss.xml'
        return

    def get_feed(self):
        ''' Gets feed from iTunes new release rss

        Gets raw feed , sends to self.parse_xml to turn into dict

        Returns True or None on success or failure (due to exception or empty movie list)
        '''

        new_albums = None

        logging.info(u'Syncing new album releases.')
        request = Url.request(self.rss)
        try:
            response = Url.open(request)
            new_albums = self.parse(response)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Unable to get iTunes rss.', exc_info=True)
            return None

        if new_albums:
            logging.info(u'Found {} new releases.'.format(len(new_albums)))
            self.sync_new_albums(new_albums)
            logging.info(u'New album sync complete.')
            return True
        else:
            return None

    def parse_xml(self, feed):
        ''' Truns xml into dict of artist and album id
        feed: itunes rss feed

        Returns list of dicts [{'artist_id': '0123456', 'album_id': '0123456'}]
        '''

        albums = []
        album = {}
        root = ET.fromstring(feed)
        itms = '{http://phobos.apple.com/rss/1.0/modules/itms/}'
        items = root[0].findall('items')

        for item in items:
            art_link = item.find(itms+'artistLink').text
            album['artist_id'] = art_link.split('id')[-1].split('?')[0]
            alb_link = item.find(itms+'albumLink').text
            album['album_id'] = alb_link.split('id')[-1].split('?')[0]
            albums.append(album)

        return albums


    def sync_new_albums(self, albums):
        ''' Adds new albums from rss feed
        :params albums: list of dicts of new album releases

        Executes ajax.add_wanted_movie() for each new imdbid

        Does not return
        '''

        artists = self.sql.get_distinct('ARTISTS', 'artist_id')
        albums = self.sql.get_distinct('ALBUMS', 'album_id')

        new_sync_albums = []
        for i in albums:
            if i['artist_id'] in artists and i['album_id'] not in albums:
                new_sync_albums.append(i)

        for artist, album in new_sync_albums.iteritems():
            album =
