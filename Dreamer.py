#!/usr/bin/python

import sys
import Queue
import urllib
import urllib2
import threading
from bs4 import BeautifulSoup

from lib.parser.OptionParser import OptionParser
from lib.parser.DomainParser import DomainParser
from lib.utils.Log import Log

class Dreamer(object):
    def __init__(self):
        self.log = Log(__name__)
        self.option = OptionParser(sys.argv)
        self.domain = DomainParser(self.option.target)
        self.finished = 0
        self.finished_lock = threading.Lock()
        self.pages = Queue.Queue()
        self.tasks = Queue.Queue()
        self.tasks.put(self.domain.domain)
    def TaskManager(self):
        for i in xrange(self.option.thread):
            t = threading.Thread(target = self.Worker,args = (self.log,self.option,self.domain))
            t.daemon = True
            t.start()
        
        # Start to manage the tasks
        wholelist = [self.domain.domain]
        whitelist = []
        while True:
            if not self.pages.empty():
                # Get the successfully retrieved page
                page = self.pages.get()
                self.log.Info2("I'm now at -> "+page[0])
                whitelist.append(page[0])

                # Analyze the page
                links = BeautifulSoup(page[1],"lxml").find_all('a')
                self.log.Info3("  this page has "+str(len(links))+" links")

                # Check whether has enough request being made
                if self.option.query != -1 and len(whitelist) >= self.option.query:
                    break

                # Put the link into tasks for Worker to work
                for link in links:
                    try:
                        link = self.domain.Append(link['href'])
                        if link != None and link not in wholelist:
                            self.tasks.put(link)
                            wholelist.append(link)
                    except:
                        self.log.Debug("This link didn't have href -> "+str(link))
                
    def Worker(self,log,option,domain):
        log = Log(str(threading.current_thread()))
        while True:
            if not self.tasks.empty():
                # Get the task
                now = self.tasks.get()

                # Try to get the page
                try:
                    response = urllib2.urlopen(urllib2.Request(now))
                except KeyboardInterrupt:
                    log.Info("You pressed Ctrl+C")
                    sys.exit(0)
                except:
                    log.Debug("I can't get this url -> "+now)
                    continue
                
                # Put the result into queue for TaskManager to analyze it
                self.pages.put((now,response))

dream = Dreamer()
try:
    dream.TaskManager()
except KeyboardInterrupt:
    dream.log.Info("You pressed Ctrl+C")
