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
        self.domain = DomainParser(self.option.target,self.option.mode)
        self.pages = Queue.Queue()
        self.tasks = Queue.Queue()
        self.tasks.put(self.domain.range)
        self.result = []

    def Run(self):
        self.TaskManager()

    def TaskManager(self):
        # Start to manage the tasks
        wholelist = [self.domain.range]
        whitelist = []
        while not self.tasks.empty() or not self.pages.empty() or threading.active_count()-1 != 0:
            # Assign new thread while threads are not enough
            if not self.tasks.empty() and threading.active_count()-1 <= self.option.thread:
                t = threading.Thread(target = self.Worker)
                t.daemon = True
                t.start()
                
            if not self.pages.empty():
                # Get the successfully retrieved page
                page = self.pages.get()
                if not self.option.quiet:
                    self.log.Info2("I'm now at -> "+page[0])
                whitelist.append(page[0])

                # Analyze the page
                soup = BeautifulSoup(page[1],"lxml")
                self.Analyzer(soup)

                # Get all links
                links = soup.find_all('a')
                if not self.option.quiet:
                    self.log.Info3("  this page has "+str(len(links))+" links")

                # Check whether has enough request being made
                if self.option.number != -1 and len(whitelist) >= self.option.number:
                    break

                # Put the link into tasks for Worker to work
                if self.option.mode == "domain" or self.option.mode == "subdomain":
                    for link in links:
                        try:
                            link = self.domain.Append(link.get('href'))
                            if link != None and link not in wholelist:
                                self.tasks.put(link)
                                wholelist.append(link)
                        except KeyboardInterrupt:
                            log.Info("You pressed Ctrl+C")
                            sys.exit(0)
                elif self.option.mode == "page":
                    pass
                else:
                    self.log.Error("I cant' recognize \""+self.option.mode+"\" mode")


    def Worker(self):
        log = Log(threading.current_thread().getName())
        while not self.tasks.empty():
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

    def Analyzer(self,soup):
        selector = self.option.tag
        for i in self.option.attribute:
            selector += "[" + i[0] + "=" + '"' + i[1] + '"' + "]"
 
        if selector != "":
            self.result += soup.select(selector)

    def Reporter(self):
        info = "Found "+str(len(self.result))+" objects"
        if self.option.tag != "" or len(self.option.attribute) != 0:
            info += " with"
        if self.option.tag != "":
            info += " tag : "+self.option.tag
        for i in self.option.attribute:
            info += ", " + i[0] + " : " + i[1]
        self.log.Info(info)
        if len(self.result) > 0:
            while True:
                yesno = raw_input("[INFO]          Would you want to print them all?(y or n)")
                if yesno == 'y':
                    for i in self.result:
                        self.log.Info3(i.get_text().strip())
                    break
                elif yesno == 'n':
                    break
                else:
                    self.log.Warning("Please type exactly 'y' or 'n'")

dream = Dreamer()

try:
    dream.Run()
except KeyboardInterrupt as error:
    dream.log.Info("You pressed Ctrl+C")
    
dream.Reporter()
