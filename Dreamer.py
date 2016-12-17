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
        if self.option.mode in ("domain","subdomain"):
            self.tasks.put((self.domain.range,self.option.header,{}))
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

                    # Get all links
                    links = soup.find_all('a')
                    if not self.option.quiet:
                        self.log.Info3("  this page has "+str(len(links))+" links")

                    # Put the link into tasks for Workers to work
                    for link in links:
                        try:
                            link = self.domain.Append(link.get('href'))
                            if link != None and link not in wholelist:
                                self.tasks.put((link,self.option.header,{}))
                                wholelist.append(link)
                        except KeyboardInterrupt:
                            log.Info("You pressed Ctrl+C")
                            sys.exit(0)

        elif self.option.mode == "repeater":
            static_parameter = {}
            parameter = []
            for item in self.option.parameter:
                if item[2] == "static":
                    static_parameter[item[0]] = item[1]
                else:
                    parameter = item
            static_data = {}
            data = []
            for item in self.option.data:
                if item[2] == "static":
                    static_data[item[0]] = item[1]
                else:
                    data = item
            counter = 0
            while not (self.option.number != -1 and counter >= self.option.number):
                # Put the link into tasks for Workers to work
                link = self.domain.range
                if parameter != []:
                    static_parameter[parameter[0]] = parameter[1]
                if data != []:
                    static_data[data[0]] = data[1]
                if static_parameter != {}:
                    link += '?'
                    suffix = ""
                    for key,value in static_parameter.iteritems():
                        suffix += key + "=" + value + "&"
                    link += suffix.rstrip('&')
 
                self.tasks.put((link,self.option.header,data))

                # Change the value
                if parameter != []:
                    if parameter[2] == "number":
                        parameter[1] = str(int(parameter[1])+1)
                elif data != []:
                    if data[2] == "number":
                        data[1] = str(int(data[1])+1)

                # Increase the counter
                counter += 1

            for i in xrange(self.option.thread):
                t = threading.Thread(target = self.Worker)
                t.daemon = True
                t.start()
                
            while not self.tasks.empty() or threading.active_count()-1 != 0:
                while not self.pages.empty():
                    # Get the successfully retrieved page
                    page = self.pages.get()
                    if not self.option.quiet:
                        self.log.Info2("I'm now at -> "+page.geturl())

                    # Analyze the page
                    soup = BeautifulSoup(page,"lxml")
                    self.Analyzer(soup)

    def Worker(self):
        log = Log(threading.current_thread().getName())
        while not self.tasks.empty():
            # Get the task
            front = self.tasks.get()
            url = front[0]
            header = front[1]
            data = front[2]

            # Try to get the page
            try:
                if header.get("User-Agent") == None:
                    header["User-Agent"] = Config.UserAgent
                if data != {}:
                    request = urllib2.Request(url,headers = header,data = data)
                else:
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
