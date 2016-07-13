import logging

#logging.config.fileConfig("logging.conf")
logger = logging.getLogger()

fh = logging.FileHandler('/tmp/test.log')
ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.setLevel(logging.DEBUG)


