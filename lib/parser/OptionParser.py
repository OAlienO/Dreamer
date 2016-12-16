import re
import sys
import getopt

from lib.utils.Log import Log

class OptionParser(object):
    def __init__(self,argv):
        self.log = Log(__name__)

        # Options
        self.quiet = False
        self.target = ""
        self.number = -1
        self.thread = -1
        self.mode = ""
        self.tag = ""
        self.attribute = []

        self.Parse(argv)

    def Usage(self):
        self.log.Info("Usage:")
        self.log.Info2("  python Dreamer.py [options] (target link)")
        self.log.Info2("Options:")
        self.log.Info2("  -h,        --help                       : See this page")
        self.log.Info2("  -q,        --quiet                      : Show only the result")
        self.log.Info2("  -n integer, --number=integer               : How many queries will be retrieved ( default : unlimited )")
        self.log.Info2("  -t integer, --thread=integer              : The maximum threads you want to use ( default : 5 )")
        self.log.Info2("  -m string, --mode=string                : Three modes as follow -> domain ,subdomain, page ( default : domain )")
        self.log.Info2("  --tag=string                            : Specify the object you want to find with tag")
        self.log.Info2("  --attr=string:string,[string:string...] : Specify the object you want to fine with attribute")

    def Parse(self,argv):
        try:
            opts,args = getopt.getopt(argv[1:],"hqn:t:m:",["help","quiet","number=","thread=","mode=","tag=","attr="])
        except getopt.GetoptError as error:
            self.log.Error("Invalid Format: "+str(error),usage = self.Usage)

        for o,a in opts:
            if o in ('-h','--help'):
                self.Usage()
                sys.exit(0)

            elif o in ('-q','--quiet'):
                self.quiet = True

            elif o in ('-n','--number'):
                try:
                    self.number = int(a)
                    if self.number <= 0:
                        raise Exception("nubmer of requests shouldn't less than or equal to zero")
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
                if a in ("domain","subdomain","page"):
                    self.mode = a
                else:
                    self.log.Error("There are only three mode : domain, subdomain, page")
            elif o in ('--tag'):
                self.tag = a
            elif o in ('--attr'):
                if re.search("^([\w-]+:[\w-]+)(,[\w-]+:[\w-]+)*$",a) != None:
                    attrlist = a.split(',')
                    for i in attrlist:
                        attr = i.split(':')
                        self.attribute.append(attr)
                else:
                    self.log.Error("Attribute format not match -> --attr=string:string[,string:string]...")
            else:
                self.log.Error("Unknown options...")

        # Set target
        if len(args) > 0:
            self.target = args[0]
        else:
            self.log.Error("You didn't specify a target",usage = self.Usage)
            
        # Default setting
        if self.thread == -1:
            self.thread = 5
        if self.mode == "":
            self.mode = "domain"
