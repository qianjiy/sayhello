from logging.handlers import TimedRotatingFileHandler
import logging


def get_logger(name='default'):
    log_filepath = r'log/data/{}.log'.format(name)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = TimedRotatingFileHandler(log_filepath,
                                       when='D',
                                       interval=1,
                                       backupCount=30)
    formatter = logging.Formatter('%(asctime)s \
    %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', )
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
