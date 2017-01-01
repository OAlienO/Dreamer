#!/usr/bin/python
import sys
import Queue
import socks
import socket
import urllib
import urllib2
import threading

from bs4 import BeautifulSoup
from cookielib import CookieJar
from stem import Signal
from stem.control import Controller

from lib.utils.Log import Log
from lib.utils.Link import Link
from lib.config.Config import Config
from lib.parser.OptionParser import OptionParser

controller = Controller.from_port(port = 9051)

def connect():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1",9050,True)
    socket.socket = socks.socksocket

def newIdentity():
    controller.authenticate(Config.torpassword)
    controller.signal(Signal.NEWNYM)

class Dreamer(object):
    def __init__(self):
        self.log = Log(__name__)
        self.option = OptionParser(sys.argv)
        # Thread Tunnel
        self.links   = Queue.Queue() # linkfinder pass to Decorator  (Link Object,url:string)
        self.tasks   = Queue.Queue() # Decorator  pass to Connector  (Link Object,url:string,header:dictionary,postdata:dictionary)
        self.pages   = Queue.Queue() # Connector  pass to LinkFinder (Link Object,page:string,url:string)
        self.data    = Queue.Queue() # Connector  pass to Analyzer   (page:string,url:string,header:dictionary,postdata:dictionary)
        # Thread Control
        self.idle = {}
        self.threads = []
        self.terminate = False
        # Thread Lock
        self.idle_lock = threading.Lock()
        # Final result
        self.object        = []
        self.vulnerability = [] # (url,header,postdata,vulnerability)

    def Run(self):
        self.Seed()
        self.threads.append(threading.Thread(target = self.LinkFinder))
        self.threads.append(threading.Thread(target = self.Decorator))
        for i in xrange(self.option.thread):
            self.threads.append(threading.Thread(target = self.Connector))
        self.threads.append(threading.Thread(target = self.Analyzer))
        for i in self.threads:
            with self.idle_lock:
                self.idle[i.name] = False
            i.daemon = True
            i.start()
        while True:
            with self.idle_lock:
                if not all([i.isAlive() for i in self.threads]) or self.links.empty() and self.tasks.empty() and self.pages.empty() and all([self.idle[i] for i in self.idle]):
                    break
        self.terminate = True

    def Seed(self):
        for i in self.option.target:
            link = Link(i[0],i[1])
            if not link.broken:
                self.links.put((link,i[0]))

    def LinkFinder(self):
        name = threading.current_thread().name
        wholelist = [i[0] for i in self.option.target]
        whitelist = []
        while not self.terminate:
            if not self.pages.empty():
                with self.idle_lock:
                    self.idle[name] = False
                # Get the pages
                try:
                    link,page,url = self.pages.get(timeout = 1)
                except:
                    continue
                # Whether has enough pages
                self.log.info2("Successfully get this url -> " + url)
                if url not in whitelist:
                    whitelist.append(url)
                if len(whitelist) >= self.option.page:
                    self.terminate = True
                    break
                # Get all links
                urls = BeautifulSoup(page,'lxml').find_all('a')
                # Put the link into tasks for Workers to work
                for i in urls:
                    i = link.absolute(i.get('href'))
                    if i and i not in wholelist:
                        self.links.put((link,i))
                        wholelist.append(i)
            else:
                with self.idle_lock:
                    self.idle[name] = True

    def Decorator(self):
        name = threading.current_thread().name
        # initialize parameter
        parameter = "?"
        parameter_key = ""
        parameter_value = 0
        for item in self.option.parameter:
            if item[2] == "static":
                parameter_string += key + "=" + value + "&"
            else:
                parameter_key = item[0]
                parameter_value = int(item[1])
        parameter = parameter.rstrip("&")
        # initialize header
        header = self.option.header
        if self.option.header.get("User-Agent") == None:
            header["User-Agent"] = Config.UserAgent
        # initialize postdata
        postdata = {}
        postdata_key = ""
        postdata_value = 0
        for item in self.option.postdata:
            postdata[item[0]] = item[1]
            if item[2] != "static":
                postdata_key = item[0]
                postdata_value = int(item[1])
        while not self.terminate:
            if not self.links.empty():
                with self.idle_lock:
                    self.idle[name] = False
                # Get the links
                try:
                    link,url = self.links.get(timeout = 1)
                except:
                    continue
                # Mutate something
                if parameter_key:
                    for i in xrange(self.option.query):
                        self.tasks.put((link,url+parameter_string+'&'+parameter_key+'='+str(int(parameter_value)+i),header,postdata))
                elif postdata_key:
                    for i in xrange(self.option.query):
                        postdata[postdata_key] = postdata_value + i
                        self.tasks.put((link,url,header,postdata))
                    postdata[postdata_key] = postdata
                else:
                    self.tasks.put((link,url,header,postdata))
            else:
                with self.idle_lock:
                    self.idle[name] = True

    def Connector(self):
        name = threading.current_thread().name
        log = Log(threading.current_thread().name)
        # Set tor connect
        if not self.option.risk:
            connect()
        # Maintain cookie
        if self.option.cookie:
            cj = CookieJar()
        while not self.terminate:
            if not self.tasks.empty():
                with self.idle_lock:
                    self.idle[name] = False
                # Get the task
                try:
                    link,url,header,postdata = self.tasks.get(timeout = 1)
                except:
                    continue
                # Try to get the page
                try:
                        # Set header and post data
                    if postdata:
                        request = urllib2.Request(url,headers = header,data = postdata)
                    else:
                        request = urllib2.Request(url,headers = header)
                    # Set cookie
                    if self.option.cookie:
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                    else:
                        opener = urllib2.build_opener()
                    # Get the response
                    response = opener.open(request)
                except KeyboardInterrupt:
                    log.info("You pressed Ctrl+C")
                    self.terminate = True
                    break
                except:
                    log.debug("I can't get this url -> " + url)
                    continue
                page = response.read()
                self.pages.put((link,page,url))
                self.data.put((page,url,header,postdata))
            else:
                with self.idle_lock:
                    self.idle[name] = True

    def Analyzer(self):
        name = threading.current_thread().name
        while not self.terminate:
            if self.data.empty():
                with self.idle_lock:
                    self.idle[name] = False
                try:
                    page,url,header,postdata = self.data.get(timeout = 1)
                except:
                    continue
                soup = BeautifulSoup(page,'lxml')
                if self.option.css:
                    self.object += soup.select(self.option.css)
                else:
                    selector = ""
                    if self.option.tag:
                        selector += self.option.tag
                    if self.option.attribute:
                        selector += "["
                        for key,value in self.option.attribute.iteritems():
                            selector += key + "=" + value + ","
                        selector = selector.rstrip(',')
                        selector += "]"
                    self.object += soup.select(selector)
            else:
                with self.idle_lock:
                    self.idle[name] = True

    def Reporter(self):
        info = "Found "+str(len(self.object))+" objects"
        if self.option.css:
            info += " with css selector : " + self.option.css
        if self.option.tag or self.option.attribute:
            info += " with"
        if self.option.tag:
            info += " tag -> " + self.option.tag
        if self.option.attribute:
            info += " attribute -> "
            for key,value in self.option.attribute.iteritems():
                info += key + " : " + value + ", "
            info = info.rstrip(', ')
        self.log.info(info)
        if len(self.object) > 0:
            while True:
                yesno = raw_input("[INFO]          Would you want to print them all?(y or n)")
                if yesno == 'y':
                    for i in self.object:
                        self.log.info3(i.get_text().strip())
                    break
                elif yesno == 'n':
                    break
                else:
                    self.log.warning("Please type exactly 'y' or 'n'")

dreamer = Dreamer()

try:
    dreamer.Run()
except KeyboardInterrupt:
    dreamer.log.info("You pressed Ctrl+C")
    dreamer.terminate = True

while dreamer.threads[-1].isAlive():
    pass
dreamer.Reporter()
