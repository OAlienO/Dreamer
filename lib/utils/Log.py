import sys
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
    def Usage(self):
        self.log.Info("Usage:")
        self.log.Info("  python Dreamer.py [options] (target link)")
        self.log.Info("  -q number, --query=number  How many queries will be retrieved")
    def Debug(self,text):
        self.logger.debug(Color.aquamarine+" "*3+text+Color.normal)
    def Info(self,text):
        self.logger.info(Color.green+" "*4+text+Color.normal)
    def Warning(self,text):
        self.logger.warning(Color.yellow+" "*1+text+Color.normal)
    def Error(self,text,usage = False):
        self.logger.error(Color.red+" "*3+text+Color.normal)
        if usage:
            self.Usage()
        sys.exit(0)
    def Critical(self,text,usage = False):
        self.logger.critical(Color.bold+Color.red+text+Color.normal)
        if usage:
            self.Usage()
        sys.exit(0)
