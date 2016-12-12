#!/usr/bin/python

import sys
import Queue
import urllib
import urllib2
from bs4 import BeautifulSoup

from lib.parser.OptionParser import OptionParser
from lib.parser.DomainParser import DomainParser
from lib.utils.Log import Log

def Spider(log,option,domain):
    result = []
    blacklist = []
    q = Queue.Queue()
    q.put(domain.link)
    while not q.empty():
        # Get a page from queue and check whether we has seen it before
        now = q.get()
        if now in result or now in blacklist:
            continue

        # Try to get the page
        try:
            response = urllib2.urlopen(urllib2.Request(now))
        except KeyboardInterrupt:
            log.Info("You pressed Ctrl+C")
            sys.exit(0)
        except:
            log.Debug("Black List -> "+now)
            blacklist.append(now)
            continue

        # Successfully Get the page
        result.append(now)
        log.Info(now)
        if option.query != -1 and len(result) >= option.query:
            break

        # Look for links
        links = BeautifulSoup(response.read(),"lxml").find_all('a')

        # Push all links into queue for further explore
        for link in links:
            try:
                link = domain.Append(link['href'])
                if link != None:
                    q.put(link)
            except:
                log.Debug("This link didn't have href -> "+str(link))

def Dream():
    log = Log(__name__)
    option = OptionParser(sys.argv)
    domain = DomainParser(option.target)
    try:
        Spider(log,option,domain)
    except KeyboardInterrupt as error:
        log.Info("You pressed Ctrl+C")
        sys.exit(0)

Dream()
