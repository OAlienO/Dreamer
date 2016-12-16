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
    def Debug(self,text):
        self.logger.debug(Color.bold+Color.aquamarine+"\t"+text+Color.normal)
    def Info(self,text):
        self.logger.info(Color.bold+Color.green+"\t\t"+text+Color.normal)
    def Info2(self,text):
        self.logger.info(Color.green+"\t\t"+text+Color.normal)
    def Info3(self,text):
        self.logger.info("\t\t"+text)
    def Warning(self,text):
        self.logger.warning(Color.bold+Color.yellow+"\t"+text+Color.normal)
    def Error(self,text,usage = None):
        self.logger.error(Color.bold+Color.red+"\t"+text+Color.normal)
        if usage:
            usage()
        sys.exit(0)
    def Error2(self,text,usage = None):
        self.logger.error(Color.red+"\t"+text+Color.normal)
        if usage:
            usage()
        sys.exit(0)
