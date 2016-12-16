import sys
import getopt

from lib.utils.Log import Log

class OptionParser(object):
    def __init__(self,argv):
        self.log = Log(__name__)

        # Options
        self.target = ""
        self.query = -1
        self.thread = -1
        self.mode = ""

        self.Parse(argv)

    def Usage(self):
        self.log.Info("Usage:")
        self.log.Info2("  python Dreamer.py [options] (target link)")
        self.log.Info2("  -h, --help : See this page")
        self.log.Info2("  -q number, --query=number : How many queries will be retrieved")
        self.log.Info2("  -t number, --thread=number : How many thread you want to use")

    def Parse(self,argv):
        try:
            opts,args = getopt.getopt(argv[1:],"hq:t:m:",["help","query=","thread=","mode="])
        except getopt.GetoptError as error:
            self.log.Error("Invalid Format: "+str(error),usage = self.Usage)
        except Exception as error:
            self.log.Error("Invalid Format: "+str(error),usage = self.Usage)

        for o,a in opts:
            if o in ('-h','--help'):
                self.Usage()
                sys.exit(0)
            elif o in ('-q','--query'):
                try:
                    self.query = int(a)
                    if self.query <= 0:
                        raise Exception("queries shouldn't less than or equal to zero")
                except ValueError as error:
                    self.log.Error(str(error))
                except Exception as error:
                    self.log.Error(str(error))
            elif o in ('-t','--thread'):
                try:
                    self.thread = int(a)
                    if self.thread <= 0:
                        raise Exception("threads shouldn't less than or equal to zero")
                except ValueError as error:
                    self.log.Error(str(error))
                except Exception as error:
                    self.log.Error(str(error))
            elif o in ('-m','--mode'):
                try:
                    self.mode = a
                    if self.mode not in ("domain","subdomain","page"):
                        raise Exception("There are only three mode : domain, subdomain, page")
                except Exception as error:
                    self.log.Error(str(error))

        # Set target
        if len(args) > 0:
            self.target = args[0]
        else:
            self.log.Error(str(error))
            
        # Default setting
        if self.thread == -1:
            self.thread = 5
        if self.mode == "":
            self.mode = "domain"
