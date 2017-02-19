import logging
import logging.handlers
import os

import core


class log(object):

    @staticmethod
    def start(path):
        """ Starts logging service
        :param path: srt path to log directory

        Does not return
        """

        if not os.path.exists(path):
            os.makedirs(path)

        logfile = os.path.join(path, 'log.txt')
        backup_days = core.CONFIG['Server']['keeplog']
        logging_level = logging.INFO

        formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(logfile, when="D", interval=1, backupCount=backup_days)
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return
