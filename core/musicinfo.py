import json
import logging
import urllib2
import os
import shutil
from core.helpers import Comparisons, Url
_k = Comparisons._k

logging = logging.getLogger(__name__)


class ITunes(object):

    def __init__(self):
        self.image_dir = os.path.join('static', 'images', 'artists', '')
        self.album_image_dir = os.path.join('static', 'images', 'albums', '')
        return

    def search_artist(self, search_term, single=False):
        ''' Search iTunes api for all matches
        search_term: str name of artist or itunes id #
        single: bool return only first result   <default False>

        Passes term to find_id or find_name depending on the data recieved.

        Returns list of dicts of individual movies from the find_x function.
        If single==True, returns dict of single result
        '''

        search_term = search_term.replace(" ", "+")

        if search_term.isdigit():
            artists = self._search_id(search_term)
        else:
            artists = self._search_name(search_term)

        if not artists or artists == ['']:
            return None
        if single is True:
            artist = artists[0]
            artist['image'] = self._get_image(artist['artistId'])
            return artist
        else:
            lst = []
            for i in artists:
                i['image'] = self._get_image(i['artistId'])
                lst.append(i)
            return lst

    def _search_name(self, name):
        ''' Search iTunes for artist name
        title: str artist name

        Returns list results, can be empty
        '''

        url = u'https://itunes.apple.com/search?term={}&media=music&entity=musicArtist&limit=3'.format(name)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = json.load(urllib2.urlopen(request))
            if response.get('resultCount') == 0:
                return ['']
            else:
                artists = response['results']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            return ['']
        return artists

    def _search_id(self, artist_id):
        ''' Search iTunes for artist id #
        id: str or int artist id number

        Returns list results, can be empty
        '''
        url = u'https://itunes.apple.com/lookup?id={}'.format(artist_id)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = json.load(urllib2.urlopen(request))
            if response.get('resultCount') == 0:
                return ['']
            else:
                return response['results']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            return ['']

    def _get_image(self, artist_id):
        ''' Gets image link for artist
        artist_id: str or int itunes artist id

        Returns str image url
        '''
        url = u'https://itunes.apple.com/lookup?id={}&entity=album&limit=1'.format(artist_id)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = json.load(urllib2.urlopen(request))
            if response.get('resultCount') < 2:
                return u'/static/images/missing.jpg'
            else:
                return response['results'][1]['artworkUrl100']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            None

    def get_albums(self, artist_id):
        ''' Gets all albums/tracks by artists
        artist_id: str artist id #

        '''

        url = u'https://itunes.apple.com/lookup?id={}&entity=album'.format(artist_id)

        request = Url.request(url)
        try:
            response = Url.open(request)
            response = json.loads(response)
            if response.get('resultCount', 0) == 0:
                return None
            else:
                albums = response['results'][1:]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            return None

        tmp = {}
        for album in albums:
            album_id = album['collectionId']
            tmp[album_id] = {'artist_id': artist_id,
                             'album_id': album_id,
                             'track_count': album['trackCount'],
                             'album_title': album['collectionName'],
                             'release_date': album['releaseDate'],
                             'image': album.get('artworkUrl100', u'/static/images/.jpg'),
                             'tracks': [],
                             'disc_count': 1
                             }
            tracks, disc_count = self.get_tracks(album_id)
            if not tracks:
                logging.error('Unable to get tracks for {}'.format(album_id))
            else:
                tmp[album_id]['tracks'] = tracks
                tmp[album_id]['disc_count'] = disc_count

        albums = []
        for i in tmp:
            albums.append(tmp[i])

        return albums

    def get_album(self, album_id):
        url = u'https://itunes.apple.com/lookup?albumId={}&entity=song'.format(album_id)

        request = Url.request(url)
        try:
            response = Url.open(request)
            response = json.loads(response)
            if response.get('resultCount', 0) == 0:
                return None
            else:
                album = response['results']
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            return None

        image_url = album[0]['artworkUrl100']

        parsed_album = {}
        tracks = album[1:]
        parsed_tracks = []
        disc_count = 1
        for track in tracks:
            if track['discCount'] > disc_count:
                disc_count = track['discCount']
            parsed_tracks.append({'title': track['trackName'],
                                  'preview_url': track['previewUrl'],
                                  'track_id': str(track['trackId']),
                                  'track_number': track['trackNumber'],
                                  'disc_number': track.get('discNumber', 1),
                                  'length': (track['trackTimeMillis'] / 1000)
                                  })

        parsed_album = {'artist_id': tracks[0]['artistId'],
                        'album_id': album_id,
                        'disc_count': disc_count,
                        'track_count': tracks[0]['trackCount'],
                        'tracks': parsed_tracks,
                        'album_title': tracks[0]['collectionName'],
                        'status': 'Wanted'
                        }

        return

    def get_tracks(self, album_id):
        ''' Gets all track info for album_id
        album_id: album id #

        Returns tuple ([{track: info}], int:disc_count)
        '''

        parsed_tracks = []

        url = u'https://itunes.apple.com/lookup?id={}&entity=song'.format(album_id)

        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = json.load(urllib2.urlopen(request))
            if response.get('resultCount') == 0:
                return None
            else:
                tracks = response['results'][1:]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'iTunes search.', exc_info=True)
            return None

        disc_count = 1
        for track in tracks:
            if track['discCount'] > disc_count:
                disc_count = track['discCount']
            parsed_tracks.append({'title': track['trackName'],
                                  'preview_url': track['previewUrl'],
                                  'track_id': str(track['trackId']),
                                  'track_number': track['trackNumber'],
                                  'disc_number': track.get('discNumber', 1),
                                  'length': (track['trackTimeMillis'] / 1000)
                                  })
        return (parsed_tracks, disc_count)


    def save_image(self, url, artist_id=None, album_id=None):
        ''' Saves image
        url: str url of image file
        artist_id: str artist id #      <optional*>
        album_id: str album id #        <optional*>

        Either arist or album id MUST be passed.

        Saves poster as autolycus/static/images/<artists|albums>/[id].jpg

        Does not return.
        '''

        if not artist_id and not album_id:
            return

        if artist_id:
            fname = '{}.jpg'.format(artist_id)
            new_image_path = os.path.join(self.image_dir, fname)
            logging.info('Saving artist image to {}.'.format(fname))
        else:
            fname = '{}.jpg'.format(album_id)
            new_image_path = os.path.join(self.album_image_dir, fname)
            logging.info('Saving album image to {}.'.format(fname))

        if os.path.exists(new_image_path) is False:
            if url == u'/static/images/missing.jpg':
                shutil.copy2(url, new_image_path)

            else:
                request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    result = urllib2.urlopen(request).read()
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    logging.error(u'Error saving image.', exc_info=True)

                try:
                    with open(new_image_path, 'wb') as output:
                        output.write(result)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e: # noqa
                    logging.error(u'Saving image write file', exc_info=True)

            logging.info(u'Image saved to {}'.format(new_image_path))
        else:
            logging.info(u'{} already exists.'.format(new_image_path))

    def remove_image(self, artist_id):
        ''' Deletes image from disk.
        :param artist_id: str artist id #

        Does not return.
        '''

        logging.info(u'Removing image for {}'.format(artist_id))
        path = u'{}{}.jpg'.format(self.image_dir, artist_id)
        if os.path.exists(path):
            os.remove(path)
        else:
            logging.info(u'{} doesn\'t seem to exist.'.format(path))
