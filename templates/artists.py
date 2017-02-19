import core
import dominate
import cherrypy
import json
from cherrypy import expose
from core import sqldb
from dominate.tags import *
from header import Header
from head import Head
from datetime import datetime
from core.helpers import Conversions


class Artists():

    def __init__(self):
        self.sql = sqldb.SQL()

    @expose
    def default(self, artist_id=None):

        if artist_id:
            return self.artist_page(artist_id, self.sql)

        doc = dominate.document(title='Autolycus')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/artists.css?v=02.07')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/artists.css?v=02.07'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/artists/main.js?v=02.02b')

        with doc:
            Header.insert_header(current="artists")
            with div(id='content'):

                self.artist_list(self.sql)

        return doc.render()

    @staticmethod
    def artist_list(sql):
        artists = sql.get_artists()

        if artists == []:
            return None
        elif not artists:
            html = 'Error retrieving artists from database. Check logs for more information'
            return html

        artist_list = ul(id='artist_list')
        with artist_list:
            for artist in artists:
                with a(href='{}/artists/{}'.format(core.URL_BASE, artist['artist_id'])):
                    with li(cls='artist', genre=artist['genre'], artist_id=artist['artist_id']):
                        img(src=artist['image'])
                        br()
                        span(artist['name'])

        return unicode(artist_list)

    @staticmethod
    def artist_page(artist_id, sql):
        artist = sql.get_artist(artist_id)
        if not artist:
            raise cherrypy.HTTPError(404, "URL not found.")

        albums = sql.get_albums(artist_id)

        doc = dominate.document(title='Autolycus')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/album_view.css?v=02.07')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/album_view.css?v=02.07'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/album_view/main.js?v=02.02b')

        with doc:
            Header.insert_header(current="artists")
            with div(id='content'):
                h1(artist['name'])

                with div(id='albums'):
                    for album in albums:
                        tracks = json.loads(album['tracks'])
                        release_date_obj = datetime.strptime(album['release_date'], '%Y-%m-%dT%H:%M:%SZ')
                        with div(id=album['album_id'], cls='album'):
                            with div(cls='overview'):
                                img(src='{}{}'.format(core.URL_BASE, album['image']))
                                div(album['album_title'], title=album['album_title'], cls='title')
                                with i() as status_icon:
                                    if album['status'] == 'ignored':
                                        status_icon['class'] = 'status_icon fa fa-square'
                                        status_icon['title'] = 'This album is not monitored and will not download.'
                                    elif album['status'] == 'wanted':
                                        status_icon['class'] = 'status_icon fa fa-circle-o'
                                        status_icon['title'] = 'This album is monitored and will be downloaded.'
                                    elif album['status'] == 'snatched':
                                        status_icon['class'] = 'status_icon fa fa-chevron-circle-down'
                                        status_icon['title'] = 'This album has been snatched and sent to your downloader.'
                                    elif album['status'] == 'finished':
                                        status_icon['class'] = 'status_icon fa fa-circle'
                                        status_icon['title'] = 'This album has been downloaded.'
                                with div(cls='info'):
                                    span('Release Date: ', cls='bold')
                                    span(Conversions.human_datetime(release_date_obj, time=False))
                                with div(cls='info'):
                                    span('Tracks: ', cls='bold')
                                    span(album['track_count'])
                                with span(cls='view_details'):
                                    i(cls='fa fa-search')
                                    i(cls='fa fa-wrench')
                                    i(cls='fa fa-chevron-circle-down view_details')

                            with div(cls='album_settings hidden'):
                                span('Status: ')
                                with select(cls='change_status'):
                                    option('Ignore', value='ignored')
                                    option('Wanted', value='wanted')
                                span('Quality: ')
                                with select(cls='change_quality'):
                                    option('fake quality')
                                    option('fake quality 2')
                                i(cls='fa fa-save')
                            with div(cls='details hidden'):
                                disc_count = album['disc_count']
                                for disc_number in range(disc_count):
                                    disc_number += 1
                                    if disc_count > 1:
                                        div('Disc {}'.format(disc_number), cls='bold')
                                    with table():
                                        for t in tracks:
                                            if t['disc_number'] == disc_number:
                                                with tr():
                                                    td(t['track_number'])
                                                    td(t['title'])
                                                    mins, secs = divmod(t['length'], 60)
                                                    td('{}:{}'.format(mins, str(secs).zfill(2)))
                                                    with td():
                                                        audio(src=t['preview_url'], preload='none')
                                                        i(cls='fa fa-play media_preview')

        return doc.render()


# pylama:ignore=W0401
