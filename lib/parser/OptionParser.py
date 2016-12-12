import sys
import getopt

from lib.utils.Log import Log

class OptionParser(object):
    def __init__(self,argv):
        self.log = Log(__name__)

        # Options
        self.target = ""
        self.query = -1

        self.Parse(argv)

    def Parse(self,argv):
        try:
            opts,args = getopt.getopt(argv[1:],"q:",["query="])
            if len(args) == 0:
                raise Exception("You didn't specify a target")
        except getopt.GetoptError as error:
            self.log.Error("Invalid Format: "+str(error),usage = True)
        except Exception as error:
            self.log.Error("Invalid Format: "+str(error),usage = True)

        self.target = args[0]
        for o,a in opts:
            if o in ('-q','--query'):
                try:
                    self.query = int(a)
                    if self.query <= 0:
                        raise Exception("queries shouldn't less than or equal to zero")
                except ValueError as error:
                    self.log.Error(str(error))
                except Exception as error:
                    self.log.Error(str(error))
