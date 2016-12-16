import re
import sys
import urllib
import urllib2

from lib.utils.Log import Log

class DomainParser(object):
    def __init__(self,link,mode):
        self.log = Log(__name__)
        self.domain = self.GetDomain(link)
        self.range = self.GetDomain(link) if mode == "domain" else link.rstrip('/')
        self.Check()
    def GetDomain(self,link):
        if re.search("^https?://",link) == None:
            return None
        head = link.find("//")
        tail = link[head+2:].find("/")
        return link if tail == -1 else link[:head+2+tail]
    def Check(self):
        try:
            response = urllib2.urlopen(urllib2.Request(self.range))
        except KeyboardInterrupt:
            self.log.Info("You pressed Ctrl+C")
            sys.exit(0)
        except urllib2.URLError as error:
            self.log.Error(str(error))
        except:
            self.log.Error("Unknown error when request to domain url")
    def Append(self,link):
        if self.GetDomain(link) == None:
            if link[0] == '#':
                return None
            if link[0] != '/':
                link = "/" + link
            if link[-1] == '/':
                link = link[:-1]
            link = self.domain + link
        if re.search("^"+self.range,link) != None:
            return link
        else:
            return None
