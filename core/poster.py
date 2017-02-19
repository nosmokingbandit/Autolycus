import logging
import os
import shutil
import urllib2
from HTMLParser import HTMLParser

logging = logging.getLogger(__name__)


class Poster():

    def __init__(self):
        self.poster_folder = u'static/images/posters/'

        if not os.path.exists(self.poster_folder):
            os.makedirs(self.poster_folder)

    def save_poster(self, imdbid, poster_url):
        ''' Saves poster locally
        :param imdbid: str imdb identification number (tt123456)
        :param poster_url: str url of poster image

        Saves poster as watcher/static/images/posters/[imdbid].jpg

        Does not return.
        '''

        logging.info(u'Grabbing poster for {}.'.format(imdbid))

        new_poster_path = u'{}{}.jpg'.format(self.poster_folder, imdbid)

        if os.path.exists(new_poster_path) is False:
            logging.info(u'Saving poster to {}'.format(new_poster_path))

            if poster_url == u'/static/images/blank_artist.jpg':
                shutil.copy2(poster_url, new_poster_path)

            else:
                request = urllib2.Request(poster_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    result = urllib2.urlopen(request).read()
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    logging.error(u'Poster save_poster get', exc_info=True)

                try:
                    with open(new_poster_path, 'wb') as output:
                        output.write(result)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e: # noqa
                    logging.error(u'Poster save_poster write', exc_info=True)

            logging.info(u'Poster saved to {}'.format(new_poster_path))
        else:
            logging.info(u'{} already exists.'.format(new_poster_path))

    def remove_poster(self, imdbid):
        ''' Deletes poster from disk.
        :param imdbid: str imdb identification number (tt123456)

        Does not return.
        '''

        logging.info(u'Removing poster for {}'.format(imdbid))
        path = u'{}{}.jpg'.format(self.poster_folder, imdbid)
        if os.path.exists(path):
            os.remove(path)
        else:
            logging.info(u'{} doesn\'t seem to exist.'.format(path))

    def find_poster(self, search_term):
        ''' Searches Yahoo images for movie poster.
        :param search_term: str movie title and date ("Movie Title 2016").

        Not used any more, but it doesn't hurt to keep it around.

        Returns str poster url.
        '''

        lParser = parseImages()

        search_term = search_term.replace(" ", "+")
        search_string = "https://images.search.yahoo.com/search/images?p={}{}".format(search_term, "+poster")

        request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

        html = urllib2.urlopen(request)

        lParser.feed(html.read().decode('utf-8'))
        lParser.close()

        return lParser.imgs[1]


class parseImages(HTMLParser):
    ''' Parse Yahoo html.

    Used to parse image links from yahoo search. Not used any more.

    '''

    def handle_starttag(self, tag, attrs):
        if tag == u'img':
            attrs = dict(attrs)
            if 'class' in attrs:
                if 'process' in attrs['class']:
                    self.imgs.append(attrs['data-src'])

    def feed(self, data):
        self.imgs = []
        HTMLParser.feed(self, data)
