import logging

from lib.utils.Color import Color
from lib.config.Config import Config

class Log(object):
    def __init__(self,name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(Config.LogLevel)
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        self.logger.addHandler(self.handler)
    def debug(self,text):
        self.logger.debug(Color.aquamarine+" "*3+text+Color.normal)
    def info(self,text):
        self.logger.info(Color.green+" "*4+text+Color.normal)
    def warning(self,text):
        self.logger.warning(Color.yellow+" "*1+text+Color.normal)
    def error(self,text):
        self.logger.error(Color.red+" "*3+text+Color.normal)
    def critical(self,text):
        self.logger.critical(Color.bold+Color.red+text+Color.normal)
