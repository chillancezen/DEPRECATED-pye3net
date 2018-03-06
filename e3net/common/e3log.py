#
#Copyright (c) 2017 Jie Zheng
#
import logging
import os
import time
from e3net.common.e3config import get_config
from e3net.common.e3config import add_config_file
from e3net.common.e3config import load_configs

default_conf = {
    'default': {
        'log_path': '/var/log/e3net/',
        'log_level': 'info'
    }
}
level_dict = {
    'notset': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

logers = dict()


def _make_sure_file_exist(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
            with open(filepath, 'w') as f:
                f.write('log file:%s created\n' % (filepath))
        except:
            return False
    return True


def _get_e3loger(filename):
    logFormatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s")
    rootLogger = logging.getLogger(filename)
    level = get_config(default_conf, 'default', 'log_level')
    path = get_config(default_conf, 'default', 'log_path')
    rootLogger.setLevel(level_dict[level])
    filepath = "{0}/{1}.log".format(path, filename)
    if _make_sure_file_exist(filepath) is False:
        return None
    fileHandler = logging.FileHandler(filepath)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.info('e3 logging started')
    return rootLogger


def get_e3loger(filename):
    global logger
    if filename in logers:
        return logers[filename]
    logger = _get_e3loger(filename)
    if logger is None:
        return None
    logers[filename] = logger
    return logger


def __test_foo():
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    logger = get_e3loger('e3vswitch')
    logger.info('hello world')
    logger.debug('hello debugging foo')
    logger1 = get_e3loger('e3vswitch1')
    logger1.info('hello world1')


if __name__ == '__main__':
    __test_foo()
    pass
