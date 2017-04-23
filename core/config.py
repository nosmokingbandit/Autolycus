import ConfigParser
import json
import logging
import random
import shutil
import core
import collections

logging = logging.getLogger(__name__)


class Config():
    ''' Config
    Config is a simple json object that is loaded into core.CONFIG as a dict

    All sections and subsections must be capitalized. All keys must be lower-case.
    No spaces, underscores, or hyphens.
    Be terse but descriptive.
    '''

    def __init__(self):
        self.configparser = ConfigParser.ConfigParser()
        self.configparser.optionxform = str

        self.file = core.CONF_FILE
        self.base_file = u'core/base_config.cfg'

    def new_config(self):
        ''' Copies base_file to config directory.

        Automatically assigns random values to searchtimehr, searchtimemin,
            installupdatehr, installupdatemin, and apikey.

        Returns str 'Config Saved' on success. Throws execption on failure.
        '''

        with open(self.base_file, 'r') as f:
            config = json.load(f)

        config['Search']['searchtimehr'] = random.randint(0, 23)
        config['Search']['searchtimemin'] = random.randint(0, 59)

        config['Server']['installupdatehr'] = random.randint(0, 23)
        config['Server']['installupdatemin'] = random.randint(0, 59)

        config['Search']['popularmovieshour'] = random.randint(0, 23)
        config['Search']['popularmoviesmin'] = random.randint(0, 59)

        apikey = "%06x" % random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        config['Server']['apikey'] = apikey

        with open(self.file, 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)
        return u'Config created at {}'.format(self.file)

    def write_dict(self, data):
        ''' Writes a dict to the config file.
        :param data: dict of Section with nested dict of keys and values:

        {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}

        MUST contain fully populated sections or data will be lost.

        Only modifies supplied section.

        After updating config file, copies to core.CONFIG via self.stash()

        Does not return.
        '''

        conf = core.CONFIG

        for k, v in data.iteritems():
            conf[k] = v

        with open(self.file, 'w') as f:
            json.dump(conf, f, indent=4, sort_keys=True)
        # After writing, copy it back to core.CONFIG
        self.stash(config=conf)
        return

    def merge_new_options(self):
        ''' Merges new options in base_config with config

        Opens base_config and config, then saves them merged with config taking priority.

        Does not return
        '''

        new_config = {}

        with open(self.base_file, 'r') as f:
            base_config = json.load(f)
        with open(self.file, 'r') as f:
            config = json.load(f)

        new_config = self._merge(base_config, config)

        with open(self.file, 'w') as f:
            json.dump(new_config, f, indent=4, sort_keys=True)

        return

    def _merge(self, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self._merge(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def stash(self, config=None):
        ''' Stores entire config as dict to core.CONFIG
        config: dict config file contents <optional>

        If 'config' is not supplied, reads config from disk. If calling stash() from
            a method in this class pass the saved config so we don't have to read from
            a file we just wrote to.

        Sanitizes input when neccesary

        Does not return
        '''

        if not config:
            with open(self.file, 'r') as f:
                config = json.load(f)

        repl = config['Postprocessing']['replaceillegal']
        if repl in ['"', '*', '?', '<', '>', '|', ':']:
            config['Postprocessing']['replaceillegal'] = ''

        core.CONFIG = config

        return

    def to_int(self, config):
        new = {}

        for k, v in config.iteritems():
            if isinstance(v, dict):
                new[k] = self.to_int(v)
            else:
                if isinstance(v, list):
                    for idx, val in enumerate(v):
                        try:
                            v[idx] = int(str(val))
                        except Exception, e: #noqa
                            v[idx] = val
                    new[k] = v
                try:
                    new[k] = int(str(v))
                except Exception, e: #noqa
                    new[k] = v
        return new
