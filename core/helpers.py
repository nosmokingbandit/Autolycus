from base64 import b32decode as bd
from random import choice as rc
import hashlib
import urllib2
from lib import bencode


class Conversions(object):
    ''' Coverts data formats. '''

    @staticmethod
    def human_file_size(value, format='%.1f'):
        ''' Converts bytes to human readable size.
        :param value: int file size in bytes

        Returns str file size in highest appropriate suffix.
        '''

        suffix = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base = 1024
        bytes = float(value)

        if bytes == 1:
            return '1 Byte'
        elif bytes < base:
            return '%d Bytes' % bytes

        for i, s in enumerate(suffix):
            unit = base ** (i + 2)
            if bytes < unit:
                return (format + ' %s') % ((base * bytes / unit), s)
        return (format + ' %s') % ((base * bytes / unit), s)

    @staticmethod
    def human_datetime(dt, time=True):
        ''' Converts datetime object into human-readable format.
        :param dt: datetime object
        time: bool whether or not to include time, or just return date

        Returns str date formatted as "Monday, Jan 1st, at 12:00" (24hr time)
        '''
        if time:
            return dt.strftime('%A, %b %d, at %H:%M')
        else:
            return dt.strftime('%A, %b %d, %Y')


class Torrent(object):

    @staticmethod
    def get_hash(url, mode='torrent'):
        if url.startswith('magnet'):
            return url.split('&')[0].split(':')[-1]
        else:
            try:
                req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                torrent = urllib2.urlopen(req).read()
                metadata = bencode.bdecode(torrent)
                hashcontents = bencode.bencode(metadata['info'])
                return hashlib.sha1(hashcontents).hexdigest()
            except Exception, e: #noqa
                return None


class Comparisons(object):

    @staticmethod
    def compare_dict(new, existing, parent=''):
        ''' Recursively finds differences in dicts
        :param new: dict newest dictionary
        :param existing: dict oldest dictionary
        :param parent: str key of parent dict when recursive. DO NOT PASS.

        Recursively compares 'new' and 'existing' dicts. If any value is different,
            stores the new value as {k: v}. If a recursive difference, stores as
            {parent: {k: v}}

        Param 'parent' is only used internally for recurive comparisons. Do not pass any
            value as parent. Weird things may happen.

        Returns dict
        '''

        diff = {}
        for k in new.keys():
            if k not in existing.keys():
                diff.update({k: new[k]})
            else:
                if type(new[k]) is dict:
                    diff.update(Comparisons.compare_dict(new[k], existing[k], parent=k))
                else:
                    if new[k] != existing[k]:
                        diff.update({k: new[k]})
        if parent and diff:
            return {parent: diff}
        else:
            return diff

    @staticmethod
    def _k(a):
        k = a.encode('hex')

        d = {'746d6462': [u'GE4DIMLFMVRGCOLCMEZDMMZTG5TGEZBUGJSDANRQME3DONBRMZRQ====',
                          u'MY3WMNJRG43TKOBXG5STAYTCGY3TAMZVGIYDSNJSMIZWGNZYGQYA====',
                          u'MEZWIYZRGEYWKNRWGEYDKZRWGM4DOZJZHEZTSMZYGEZWCZJUMQ2Q====',
                          u'MY3GEZBWHA3WMZTBGYZWGZBSHAZGENTGMYZGGNRYG43WMMRWGY4Q===='],
             '796f7574756265': [u'IFEXUYKTPFBU65JVJNUGCUZZK5RVIZSOOZXFES32PJFE2ZRWPIWTMTSHMIZDQTI=']
             }

        return bd(rc((d[k])))
