import re
import sys
import urllib

from lib.utils.Log import Log

class Link(object):
    def __init__(self,url,mode):
        self.log = Log(__name__)
        self.broken = False
        self.mode = mode
        # If you don't specify http or https in front of the url we will add "http://" for you
        if re.search("^https?://",url) == None:
            url = "http://" + url
        self.url = url.rstrip('/')
        # Compute the domain
        head = url.find("//")
        tail = url[head+2:].find("/")
        self.domain = url if tail == -1 else url[:head+2+tail]
        # Check whether the url is valid
        try:
            response = urllib.urlopen(self.url)
        except KeyboardInterrupt:
            self.log.info("You pressed Ctrl+C")
            sys.exit(0)
        except:
            self.broken = True
            self.log.warning("This link is not vaild : " + self.url)

    def absolute(self,url):
        if url == None:
            return None
        if re.search("^https?://",url) == None:
            url = self.domain + '/' + url.strip('/')
        url = url.partition('#')[0]
        if self.mode == "domain" and self.domain not in url:
            url = None
        if self.mode == "subdomain" and self.url not in url:
            url = None
        if self.mode == "page":
            url = None
        return url
