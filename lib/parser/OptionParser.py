import re
import sys
import getopt

from lib.utils.Log import Log

class OptionParser(object):
    def __init__(self,argv):
        self.log = Log(__name__)
        # Options
        self.target    = []    # (url:string,mode:string)
        self.quiet     = False
        self.mode      = ""
        self.page      = -1
        self.query     = -1
        self.parameter = []    # [key,value,mode]
        self.header    = {}    # key: value
        self.postdata  = []    # [key,value,mode]
        self.tag       = ""
        self.attribute = {}    # key: value
        self.css       = ""
        self.thread    = -1
        self.cookie    = False
        self.risk      = False
        # Parse the options
        self.parse(argv)

    def usage(self):
        self.log.info("Usage:")
        self.log.info2("  python Dreamer.py [options] (target link)")
        self.log.info("Options:")
        self.log.info2("  General:")
        self.log.info2("    -h,--help                         : See this page")
        self.log.info2("    -q,--quiet                        : Show only the result")
        self.log.info2("  LinkFinder:")
        self.log.info2("    --mode=string                     : Three modes as follow -> domain ,subdomain, page ( default : domain )")
        self.log.info2("    --page=integer                    : How many pages will be retrieved ( default : unlimited )")
        self.log.info2("  Decorator:")
        self.log.info2("    --query=integer                   : How many queries will be requested by a single page ( default : 50 )")
        self.log.info2("    --parameter=key:value:mode[,...]  : Set url parameter, two modes as follow -> static, number")
        self.log.info2("    --header=key:value[,...]          : Set the header field")
        self.log.info2("    --postdata=key:value:mode[,...]   : Set post data you want to send, two modes as follow -> static, number")
        self.log.info2("  Connector:")
        self.log.info2("    --thread=integer                  : The threads to you want to use ( default : 5 )")
        self.log.info2("    --cookie                          : Maintain the cookie")
        self.log.info2("    --risk                            : Disable the tor and make yourself at risk")
        self.log.info2("  Analyzer:")
        self.log.info2("    --tag=string                      : Specify the object you want to find with tag")
        self.log.info2("    --attribute=name:value[,...]      : Specify the object you want to find with attribute")
        self.log.info2("    --css=string                      : Specify the object you want to find with css selector")

    def parse(self,argv):
        try:
            opts,args = getopt.getopt(argv[1:],"hq",["help","quiet","mode=","page=","query=","parameter=","header=","postdata=","tag=","attribute=","css=","thread=","cookie","risk"])
        except getopt.GetoptError as error:
            self.log.error("Invalid Format: "+str(error),usage = self.usage)

        for o,a in opts:
            # --help
            if o in ('-h','--help'):
                self.usage()
                sys.exit(0)
            # -q --quiet
            elif o in ('-q','--quiet'):
                self.quiet = True
            # --mode
            elif o in ('--mode'):
                if a in ("domain","subdomain","page"):
                    self.mode = a
                else:
                    self.log.error("There are only three mode : domain, subdomain, page")
            # --page
            elif o in ('--page'):
                try:
                    self.page = int(a)
                    if self.page <= 0:
                        self.log.error(str("nubmer of requests shouldn't less than or equal to zero"))
                except Valueerror as error:
                    self.log.error(str(error))
            # --query
            elif o in ('--query'):
                try:
                    self.query = int(a)
                    if self.query <= 0:
                        self.log.error(str("nubmer of requests shouldn't less than or equal to zero"))
                except Valueerror as error:
                    self.log.error(str(error))
            # --parameter
            elif o in ('--parameter'):
                if re.search("^([^:,]+:[^:,]+:[^:,]+)(,[^:,]+:[^:,]+:[^:,]+)*$",a) == None:
                    self.log.error("Attribute format not match -> --parameter=key:value:mode[,...]")
                attrlist = a.split(',')
                for i in attrlist:
                    attr = i.split(':')
                    if attr[2] not in ("static","number"):
                        self.log.error("We do not support "+attr[2]+" mode in --parameter")
                    if attr[2] == "number":
                        try:
                            _ = int(attr[2])
                        except:
                            self.log.error("You told me it is number mode but it's not a number")
                    self.parameter.append(attr)
            # --header
            elif o in ('--header'):
                if re.search("^([^:,]+:[^:,]+)(,[^:,]+:[^:,]+)*$",a) != None:
                    attrlist = a.split(',')
                    for i in attrlist:
                        attr = i.split(':')
                        self.header[attr[0]] = attr[1]
                else:
                    self.log.error("Attribute format not match -> --header=string:string[,...]")
            # --postdata
            elif o in ('--postdata'):
                if re.search("^([^:,]+:[^:,]+:[^:,]+)(,[^:,]+:[^:,]+:[^:,]+)*$",a) == None:
                    self.log.error("Attribute format not match -> --postdata=key:value:mode[,...]")
                attrlist = a.split(',')
                for i in attrlist:
                    attr = i.split(':')
                    if attr[2] not in ("static","number"):
                        self.log.error("We do not support "+attr[2]+" mode in --postdata")
                    if attr[2] == "number":
                        try:
                            _ = int(attr[2])
                        except:
                            self.log.error("You told me it is number mode but it's not a number")
                    self.postdata.append(attr)
            # --thread
            elif o in ('--thread'):
                try:
                    self.thread = int(a)
                    if self.thread <= 0:
                        raise Exception("threads shouldn't less than or equal to zero")
                except Valueerror as error:
                    self.log.error(str(error))
                except Exception as error:
                    self.log.error(str(error))
            # --cookie
            elif o in ('--cookie'):
                self.cookie = True
            # --risk
            elif o in ('--risk'):
                self.risk = True
            # --tag
            elif o in ('--tag'):
                self.tag = a
            # --attribute
            elif o in ('--attribute'):
                if re.search("^([^:,]+:[^:,]+)(,[^:,]+:[^:,]+)*$",a) != None:
                    attrlist = a.split(',')
                    for i in attrlist:
                        attr = i.split(':')
                        self.attribute[attr[0]] = attr[1]
                else:
                    self.log.error("Attribute format not match -> --attribute=string:string[,...]")
            # --css
            elif o in ('--css'):
                self.css = a
            # unknown option ( shouldn't happened )
            else:
                self.log.error("Unknown options...")

        # Default setting
        if self.mode == "":
            self.mode = "domain"
        if self.query == -1:
            self.query = 50
        if self.thread == -1:
            self.thread = 5

        # Set target
        if len(args) > 0:
            try:
                f = open(args[0],'r')
                for index,line in enumerate(f):
                    line = line.split(" ")
                    if len(line) > 2:
                        self.log.error("Wrong format in " + args[0] + " line " + index)
                    elif line[1] not in ("domain","subdomain","page"):
                        self.log.error("Unknown mode: " + line[0] + " in " + args[0] + " line " + index)
                    self.target.append((line[0].rstrip('/'),line[1]))
                f.close()
            except:
                self.target.append((args[0].rstrip('/'),self.mode))
        else:
            self.log.error("You didn't specify a target",usage = self.usage)

        # Check
        if self.css != "" and (self.tag != "" or self.attribute != {}):
            self.log.error("--tag and --attr should not be use together with --css")
