import datetime
import json
import logging
import os
import sys
import threading

import cherrypy
import core
from core import config, library, newznab, plugins, musicinfo, scoreresults, searcher, snatcher, sqldb, torrent, updatestatus, version
from core.downloaders import nzbget, sabnzbd, transmission, qbittorrent, deluge
from core.musicinfo import ITunes
from core.notification import Notification
from core.rss import predb
from templates import movie_info_popup, movie_status_popup, plugin_conf_popup, status

logging = logging.getLogger(__name__)


class Ajax(object):
    ''' These are all the methods that handle
        ajax post/get requests from the browser.

    Except in special circumstances, all should return a string
        since that is the only datatype sent over http

    '''

    def __init__(self):
        self.itunes = ITunes()
        self.config = config.Config()
        self.library = library.ImportDirectory()
        self.predb = predb.PreDB()
        self.plugins = plugins.Plugins()
        self.searcher = searcher.Searcher()
        self.score = scoreresults.ScoreResults()
        self.sql = sqldb.SQL()
        self.musicinfo = musicinfo.ITunes()
        self.snatcher = snatcher.Snatcher()
        self.update = updatestatus.Status()

    @cherrypy.expose
    def search_itunes(self, search_term):
        ''' Search tmdb for movies
        :param search_term: str title and year of movie (Movie Title 2016)

        Returns str json-encoded list of dicts that contain tmdb's data.
        '''

        results = self.itunes.search_artist(search_term)
        if not results:
            logging.info(u'No Results found for {}'.format(search_term))
            return None
        else:
            return json.dumps(results)

    @cherrypy.expose
    def movie_info_popup(self, data):
        ''' Calls movie_info_popup to render html
        :param imdbid: str imdb identification number (tt123456)

        Returns str html content.
        '''

        mip = movie_info_popup.MovieInfoPopup()
        return mip.html(data)

    @cherrypy.expose
    def movie_status_popup(self, imdbid):
        ''' Calls movie_status_popup to render html
        :param imdbid: str imdb identification number (tt123456)

        Returns str html content.
        '''

        msp = movie_status_popup.MovieStatusPopup()
        return msp.html(imdbid)

    @cherrypy.expose
    def add_artist(self, data):
        ''' Adds artist to library
        :param data: str json.dumps(dict) of info to add to database.

        Writes data to ARTISTS table.

        Returns str json.dumps(dict) of status and message
        '''

        data = json.loads(data)
        data['name'] = data.pop('artistName')
        data['artist_id'] = artist_id = data.pop('artistId')
        data['amgid'] = data.pop('amgartistId', None)
        data['link'] = data.pop('artistLinkUrl')
        data['genre'] = data.pop('primaryGenreName')

        response = {}

        TABLE = u'ARTISTS'

        if self.sql.row_exists(TABLE, artist_id=data['artist_id']):
            logging.info(u'{} already in library.'.format(data['name']))
            response['response'] = False
            response['error'] = u'{} is already in library.'.format(data['name'])
            return json.dumps(response)

        image_url = data['image']

        data['image'] = u'/static/images/artists/{}.jpg'.format(data['artist_id'])

        required_keys = ['name', 'artist_id', 'amgid', 'link', 'genre', 'image']
        db_data = {}
        for k, v in data.iteritems():
            if k in required_keys:
                db_data[k] = v

        if not self.sql.write(TABLE, db_data):
            response['response'] = False
            response['error'] = u'Could not write to database. ' \
                'Check logs for more information.'
            return json.dumps(response)

        else:
            td_get_image = threading.Thread(target=self.musicinfo.save_image,
                                            args=(image_url,), kwargs={'artist_id': artist_id})
            td_get_image.start()

            albums = self.musicinfo.get_albums(artist_id)

            for album in albums:
                album['status'] = 'ignored'
                album['tracks'] = json.dumps(album.pop('tracks'))
                td_get_album_image = threading.Thread(target=self.musicinfo.save_image,
                                                      args=(album['image'],), kwargs={'album_id': album['album_id']})
                td_get_album_image.start()
                album['image'] = u'/static/images/albums/{}.jpg'.format(album['album_id'])

            self.sql.write_albums(albums)

            response['response'] = True
            response['message'] = u'{} added to library.'.format(data['name'])

            # self.plugins.added()

            return json.dumps(response)

    @cherrypy.expose
    def add_wanted_imdbid(self, imdbid, quality='Default'):
        ''' Method to quckly add movie with just imdbid
        :param imdbid: str imdb id #

        Submits movie with base quality options

        Generally just used for the api

        Returns dict of success/fail with message.

        Returns str json.dumps(dict)
        '''

        response = {}

        data = self.tmdb._search_imdbid(imdbid)

        if not data:
            response['status'] = u'false'
            response['message'] = u'{} not found on TMDB.'.format(imdbid)
            return response
        else:
            data = data[0]

        data['quality'] = quality

        return self.add_wanted_movie(json.dumps(data))

    @cherrypy.expose
    def save_settings(self, data):
        ''' Saves settings to config file
        :param data: dict of Section with nested dict of keys and values:
        {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}

        All dicts must contain the full tree or data will be lost.

        Fires off additional methods if neccesary.

        Returns json.dumps(dict)
        '''

        orig_config = dict(core.CONFIG)

        logging.info(u'Saving settings.')
        data = json.loads(data)

        save_data = {}
        for key in data:
            if data[key] != core.CONFIG[key]:
                save_data[key] = data[key]

        if not save_data:
            return json.dumps({'response': True})

        try:
            self.config.write_dict(save_data)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e: # noqa
            logging.error(u'Writing config.', exc_info=True)
            return json.dumps({'response': False, 'error': 'Unable to write to config file.'})

        return json.dumps({'response': True})

    @cherrypy.expose
    def remove_movie(self, imdbid):
        ''' Removes movie
        :param imdbid: str imdb identification number (tt123456)

        Removes row from MOVIES, removes any entries in SEARCHRESULTS
        In separate thread deletes poster image.

        Returns srt 'error' or nothing on success
        '''

        t = threading.Thread(target=self.poster.remove_poster, args=(imdbid,))
        t.start()

        if self.sql.remove_movie(imdbid):
            response = {'response': True}
        else:
            response = {'response': False}
        return json.dumps(response)

    @cherrypy.expose
    def search(self, imdbid, title, year, quality):
        ''' Search indexers for specific movie.
        :param imdbid: str imdb identification number (tt123456)
        :param title: str movie title and year

        Checks predb, then, if found, starts searching providers for movie.

        Does not return
        '''

        self.searcher.search(imdbid, title, year, quality)
        return

    @cherrypy.expose
    def manual_download(self, title, year, guid, kind):
        ''' Sends search result to downloader manually
        :param guid: str download link for nzb/magnet/torrent file.
        :param kind: str type of download (torrent, magnet, nzb)

        Returns str json.dumps(dict) success/fail message
        '''

        torrent_enabled = core.CONFIG['Downloader']['Sources']['torrentenabled']

        usenet_enabled = core.CONFIG['Downloader']['Sources']['usenetenabled']

        if kind == 'nzb' and not usenet_enabled:
            return json.dumps({'response': False, 'error': 'Link is NZB but no Usent downloader is enabled.'})
        if kind in ['torrent', 'magnet'] and not torrent_enabled:
            return json.dumps({'response': False, 'error': 'Link is {} but no Torrent downloader is enabled.'.format(kind)})

        data = dict(self.sql.get_single_search_result('guid', guid))
        if data:
            data['year'] = year
            return json.dumps(self.snatcher.snatch(data))
        else:
            return json.dumps({'response': False, 'error': 'Unable to get download '
                               'information from the database. Check logs for more information.'})

    @cherrypy.expose
    def mark_bad(self, guid, imdbid):
        ''' Marks guid as bad in SEARCHRESULTS and MARKEDRESULTS
        :param guid: srt guid to mark

        Returns str json.dumps(dict)
        '''

        if self.update.mark_bad(guid, imdbid=imdbid):
            response = {'response': True, 'message': 'Marked as Bad.'}
        else:
            response = {'response': False, 'error': 'Could not mark release as bad. '
                        'Check logs for more information.'}

        return json.dumps(response)

    @cherrypy.expose
    def notification_remove(self, index):
        ''' Removes notification from core.notification
        :param index: str or unicode index of notification to remove

        'index' will be a type of string since it comes from ajax request.
            Therefore we convert to int here before passing to Notification

        Simply calls Notification module.

        Does not return
        '''

        Notification.remove(int(index))

        return

    @cherrypy.expose
    def update_check(self):
        ''' Manually check for updates

        Returns str json.dumps(dict) from Version manager update_check()
        '''

        response = version.Version().manager.update_check()
        return json.dumps(response)

    @cherrypy.expose
    def refresh_list(self, list, imdbid='', quality=''):
        ''' Re-renders html for Movies/Results list
        :param list: str the html list id to be re-rendered
        :param imdbid: str imdb identification number (tt123456) <optional>

        Calls template file to re-render a list when modified in the database.
        #result_list requires imdbid.

        Returns str html content.
        '''

        if list == u'#movie_list':
            return status.Status.movie_list()
        if list == u'#result_list':
            return movie_status_popup.MovieStatusPopup().result_list(imdbid, quality)

    @cherrypy.expose
    def test_downloader_connection(self, mode, data):
        ''' Test connection to downloader.
        :param mode: str which downloader to test.
        :param data: dict connection information (url, port, login, etc)

        Executes staticmethod in the chosen downloader's class.

        Returns str json.dumps dict:
        {'status': 'false', 'message': 'this is a message'}
        '''

        response = {}

        data = json.loads(data)

        if mode == u'sabnzbd':
            test = sabnzbd.Sabnzbd.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test
        if mode == u'nzbget':
            test = nzbget.Nzbget.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test

        if mode == u'transmission':
            test = transmission.Transmission.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test

        if mode == u'delugerpc':
            test = deluge.DelugeRPC.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test

        if mode == u'delugeweb':
            test = deluge.DelugeWeb.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test

        if mode == u'qbittorrent':
            test = qbittorrent.QBittorrent.test_connection(data)
            if test is True:
                response['status'] = True
                response['message'] = u'Connection successful.'
            else:
                response['status'] = False
                response['error'] = test

        return json.dumps(response)

    @cherrypy.expose
    def server_status(self, mode):
        ''' Check or modify status of CherryPy server_status
        :param mode: str command or request of state

        Restarts or Shuts Down server in separate thread.
            Delays by one second to allow browser to redirect.

        If mode == u'online', asks server for status.
            (ENGINE.started, ENGINE.stopped, etc.)

        Returns nothing for mode == restart || shutdown
        Returns str server state if mode == online
        '''

        def server_restart():
            cwd = os.getcwd()
            cherrypy.engine.restart()
            os.chdir(cwd)  # again, for the daemon
            return

        def server_shutdown():
            cherrypy.engine.stop()
            cherrypy.engine.exit()
            sys.exit(0)

        if mode == u'restart':
            logging.info(u'Restarting Server...')
            threading.Timer(1, server_restart).start()
            return

        elif mode == u'shutdown':
            logging.info(u'Shutting Down Server...')
            threading.Timer(1, server_shutdown).start()
            return

        elif mode == u'online':
            return str(cherrypy.engine.state)

    @cherrypy.expose
    def update_now(self, mode):
        ''' Starts and executes update process.
        :param mode: str 'set_true' or 'update_now'

        The ajax response is a generator that will contain
            only the success/fail message.

        This is done so the message can be passed to the ajax
            request in the browser while cherrypy restarts.
        '''

        response = self._update_now(mode)
        for i in response:
            return i

    @cherrypy.expose
    def _update_now(self, mode):
        ''' Starts and executes update process.
        :param mode: str 'set_true' or 'update_now'

        Helper for self.update_now()

        If mode == set_true, sets core.UPDATING to True
        This is done so if the user visits /update without setting true
            they will be redirected back to status.
        Yields 'true' back to browser

        If mode == u'update_now', starts update process.
        Yields 'true' or 'failed'. If true, restarts server.
        '''

        if mode == u'set_true':
            core.UPDATING = True
            yield json.dumps({'response': True})
        if mode == u'update_now':
            update_status = version.Version().manager.execute_update()
            core.UPDATING = False
            if update_status is False:
                logging.info(u'Update Failed.')
                yield json.dumps({'response': False})
            elif update_status is True:
                yield json.dumps({'response': True})
                logging.info(u'Respawning process...')
                cherrypy.engine.stop()
                python = sys.executable
                os.execl(python, python, * sys.argv)
        else:
            return

    @cherrypy.expose
    def update_movie_options(self, quality, status, imdbid):
        ''' Updates quality settings for individual title
        :param quality: str name of new quality
        :param status: str status management state
        :param imdbid: str imdb identification number

        '''

        logging.info(u'Updating quality profile to {} for {}.'.format(quality, imdbid))

        if not self.sql.update('MOVIES', 'quality', quality, imdbid=imdbid):
            return json.dumps({'response': False})

        logging.info(u'Updating status to {} for {}.'.format(status, imdbid))

        if status == 'Automatic':
            if not self.update.movie_status(imdbid):
                return json.dumps({'response': False})
        elif status == 'Finished':
            if not self.sql.update('MOVIES', 'status', 'Disabled', imdbid=imdbid):
                return json.dumps({'response': False})

        return json.dumps({'response': True})

    @cherrypy.expose
    def get_log_text(self, logfile):

        with open(os.path.join(core.LOG_DIR, logfile), 'r') as f:
            log_text = f.read()

        return log_text

    @cherrypy.expose
    def indexer_test(self, indexer, apikey, mode):
        if mode == 'newznab':
            return json.dumps(newznab.NewzNab.test_connection(indexer, apikey))
        elif mode == 'potato':
            return json.dumps(torrent.Torrent.test_potato_connection(indexer, apikey))
        else:
            return None

    @cherrypy.expose
    def get_plugin_conf(self, folder, conf):
        ''' Calls plugin_conf_popup to render html
        folder: str folder to read config file from
        conf: str filename of config file (ie 'my_plugin.conf')

        Returns str html content.
        '''

        return plugin_conf_popup.PluginConfPopup.html(folder, conf)

    @cherrypy.expose
    def save_plugin_conf(self, folder, conf, data):
        ''' Calls plugin_conf_popup to render html
        folder: str folder to store config file
        conf: str filename of config file (ie 'my_plugin.conf')
        data: str json data to store in conf file

        Returns str json dumps dict of success/fail message
        '''

        data = json.loads(data)

        conf_file = conf_file = os.path.join(core.PROG_PATH, core.PLUGIN_DIR, folder, conf)

        response = {'response': True, 'message': 'Plugin settings saved'}

        try:
            with open(conf_file, 'w') as output:
                json.dump(data, output, indent=2)
        except Exception, e: #noqa
            response = {'response': False, 'error': str(e)}

        return json.dumps(response)

    @cherrypy.expose
    def scan_library(self, directory, minsize, recursive):
        ''' Calls library to scan directory for movie files
        directory: str directory to scan
        minsize: str minimum file size in mb, coerced to int
        resursive: str 'true' or 'false', coerced to bool

        Removes all movies already in library.

        returns str json.dumps dict. Keys = filepaths, values = dict of metadata
        '''

        recursive = bool(recursive)
        minsize = int(minsize)

        movies = self.library.scan_dir(directory, minsize, recursive)

        if not movies:
            return json.dumps({})

        library = [i['imdbid'] for i in self.sql.get_user_movies()]

        new_movies = {k: v for k, v in movies.iteritems() if v['imdbid'] not in library}

        return json.dumps(new_movies)

    @cherrypy.expose
    def submit_import(self, movie_data, corrected_movies):
        ''' Imports list of movies in data
        movie_data: list of dicts of movie info ready to import
        corrected_movies: list of dicts of user-corrected movie info

        corrected_movies must be [{'/path/to/file': {'known': 'metadata'}}]

        Iterates through corrected_movies and attmpts to get metadata again.

        If imported, generates and stores fake search result.

        Created dict {'success': [], 'failed': []} and
            appends movie data to the appropriate list.

        Returns json-formatted dict described above.
        '''

        movie_data = json.loads(movie_data)
        corrected_movies = json.loads(corrected_movies)

        fake_results = []

        results = {'success': [], 'failed': []}

        if corrected_movies:
            for filepath, data in corrected_movies.iteritems():
                data['filepath'] = filepath
                tmdbdata = self.tmdb.search(data['imdbid'], single=True)
                if tmdbdata:
                    data['year'] = tmdbdata['release_date'][:4]
                    data.update(tmdbdata)
                    movie_data.append(data)
                else:
                    data['error'] = 'Unable to find "{}" on TMDB.'.format(data['imdbid'])
                    results['failed'].append(data)

        for movie in movie_data:
            if movie['imdbid']:
                movie['status'] = 'Disabled'
                response = json.loads(self.add_wanted_movie(json.dumps(movie)))
                if response['response'] is True:
                    results['success'].append(movie)
                    fake_results.append(self.library.fake_search_result(movie))
                else:
                    movie['error'] = response['error']
                    results['failed'].append(movie)
            else:
                movie['error'] = "IMDB ID not supplied."
                results['failed'].append(movie)

        fake_results = self.score.score(fake_results, quality_profile='import')

        for i in results['success']:
            score = None
            for r in fake_results:
                if r['imdbid'] == i['imdbid']:
                    score = r['score']
                    break
            if score:
                self.sql.update('MOVIES', 'finished_score', score, imdbid=i['imdbid'])

        self.sql.write_search_results(fake_results)

        return json.dumps(results)
