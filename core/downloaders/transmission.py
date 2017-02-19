import logging

from lib import transmissionrpc

import core

logging = logging.getLogger(__name__)


class Transmission(object):

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to Transmission
        data: dict of Transmission server information

        Return True on success or str error message on failure
        '''

        host = data['host']
        port = data['port']
        user = data['user']
        password = data['pass']

        try:
            client = transmissionrpc.Client(host, port, user=user, password=password)
            if type(client.rpc_version) == int:
                return True
            else:
                return 'Unable to connect.'
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Transmission test_connection', exc_info=True)
            return '{}.'.format(e)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to Transmission
        data: dict of torrrent/magnet information

        Adds torrents to /default/path/<category>

        Returns dict {'response': True, 'download_id': 'id'}
                     {'response': False', 'error': 'exception'}

        '''

        conf = core.CONFIG['Downloader']['Torrent']['Transmission']

        host = conf['host']
        port = conf['port']
        user = conf['user']
        password = conf['pass']

        client = transmissionrpc.Client(host, port, user=user, password=password)

        url = data['torrentfile']
        paused = conf['addpaused']
        bandwidthPriority = conf['priority']
        category = conf['category']

        priority_keys = {
            'Low': '-1',
            'Normal': '0',
            'High': '1'
        }

        bandwidthPriority = priority_keys[conf['priority']]

        download_dir = None
        if category:
            d = client.get_session().__dict__['_fields']['download_dir'][0]
            d_components = d.split('/')
            d_components.append(category)

            download_dir = '/'.join(d_components)

        try:
            download = client.add_torrent(url, paused=paused, bandwidthPriority=bandwidthPriority, download_dir=download_dir, timeout=30)
            download_id = download.hashString
            return {'response': True, 'downloadid': download_id}
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'Transmission add_torrent', exc_info=True)
            return {'response': False, 'error': str(e)}
