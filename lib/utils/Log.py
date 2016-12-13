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
        self.logger.debug(Color.bold+Color.aquamarine+" "*2+text+Color.normal)
    def Info(self,text):
        self.logger.info(Color.bold+Color.green+" "*3+text+Color.normal)
    def Info2(self,text):
        self.logger.info(Color.green+" "*3+text+Color.normal)
    def Info3(self,text):
        self.logger.info(" "*3+text)
    def Warning(self,text):
        self.logger.warning(Color.bold+Color.yellow+text+Color.normal)
    def Error(self,text,usage = False):
        self.logger.error(Color.bold+Color.red+" "*2+text+Color.normal)
        if usage:
            self.Usage()
        sys.exit(0)
    def Error2(self,text,usage = False):
        self.logger.error(Color.red+" "*2+text+Color.normal)
        if usage:
            self.Usage()
        sys.exit(0)
