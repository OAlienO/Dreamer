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
from lib.config.Config import Config

class Dreamer(object):
    def __init__(self):
        self.log = Log(__name__)
        self.option = OptionParser(sys.argv)
        self.domain = DomainParser(self.option.target,self.option.mode)
        self.pages = Queue.Queue()
        self.tasks = Queue.Queue()
        self.result = []

    def Run(self):
        self.TaskManager()

    def TaskManager(self):
        # Start to manage the tasks
        if self.option.mode in ("domain","subdomain"):
            self.tasks.put((self.domain.range,self.option.header))
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
                    self.log.Info2("I'm now at -> "+page.geturl())
                whitelist.append(page.geturl())

                # Analyze the page
                soup = BeautifulSoup(page,"lxml")
                self.Analyzer(soup)

                # Check whether has enough request being made
                if self.option.number != -1 and len(whitelist) >= self.option.number:
                    break

                if self.option.mode in ("domain","subdomain"):
                    # Get all links
                    links = soup.find_all('a')
                    if not self.option.quiet:
                        self.log.Info3("  this page has "+str(len(links))+" links")

                    # Put the link into tasks for Worker to work
                    for link in links:
                        try:
                            link = self.domain.Append(link.get('href'))
                            if link != None and link not in wholelist:
                                self.tasks.put((link,self.option.header))
                                wholelist.append(link)
                        except KeyboardInterrupt:
                            log.Info("You pressed Ctrl+C")
                            sys.exit(0)
                elif self.option.mode == "repeater":
                    pass
                else:
                    self.log.Error("I cant' recognize \""+self.option.mode+"\" mode")


    def Worker(self):
        log = Log(threading.current_thread().getName())
        while not self.tasks.empty():
            # Get the task
            front = self.tasks.get()
            url = front[0]
            header = front[1]

            # Try to get the page
            try:
                if header.get("User-Agent") == None:
                    header["User-Agent"] = Config.UserAgent
                request = urllib2.Request(url,headers = header)
                opener = urllib2.build_opener()
                response = opener.open(request)
            except KeyboardInterrupt:
                log.Info("You pressed Ctrl+C")
                sys.exit(0)
            except:
                log.Debug("I can't get this url -> "+url)
                continue
            
            # Put the result into queue for TaskManager to analyze it
            self.pages.put(response)

    def Analyzer(self,soup):
        selector = ""
        if self.option.css != "":
            selector = self.option.css
        else:
            selector = self.option.tag
            for key,value in self.option.attribute:
                selector += "[" + key + "=" + '"' + value + '"' + "]"
 
        if selector != "":
            self.result += soup.select(selector)

    def Reporter(self):
        info = "Found "+str(len(self.result))+" objects"
        if self.option.css != "":
            info += " with css selector : " + self.option.css
        elif self.option.tag != "" or len(self.option.attribute) != 0:
            info += " with"
            if self.option.tag != "":
                info += " tag : "+self.option.tag
            for key,value in self.option.attribute:
                info += ", " + key + " : " + value
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
