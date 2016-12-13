import re
import urllib
import urllib2

from lib.utils.Log import Log

class DomainParser(object):
    def __init__(self,link):
        self.log = Log(__name__)
        self.domain = self.GetDomain(link)
        self.Check()
    def GetDomain(self,link):
        if re.search("^https?://",link) == None:
            return None
        head = link.find("//")
        tail = link[link.find("//")+2:].find("/")
        return link if tail == -1 else link[:head+2+tail]
    def Check(self):
        try:
            response = urllib2.urlopen(urllib2.Request(self.domain))
        except urllib2.URLError as error:
            self.log.error(str(error))
        except:
            self.log.error("Unknown error when request to domain url")
    def Append(self,link):
        domain = self.GetDomain(link)
        if domain == None:
            return self.domain + link if link[0] != '#' else None
        # Under the same domain
        elif domain == self.domain:
            return link
        else:
            return None
