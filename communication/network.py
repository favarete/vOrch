from urllib2 import Request
import urllib2
import socket
import register
import _global_

CACHE_ADDRESS = "communication/cache.txt"
TIMEOUT_VALUE = 5

class SendCommand():

    def __init__(self, ID, IP):
        self.ID = ID
        self.IP = IP

    def formatString(self, value):
        z = ""
        i = 0
        for i in range(5-len(str(value))):
            z = z+"0"
        return z+str(value)

    def rotateLeft(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/rotateLeft"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"

    def rotateRight(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/rotateRight"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"

    def moveForward(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/moveForward"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"

    def moveBack(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/moveBack"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"

    def invert(self):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/invert", timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"
                               
    def shiftUp(self):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/shiftUp", timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"
                               
    def shiftDown(self):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/shiftDown", timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"
                               
    def configDelay(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/configDelay"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"
                               
    def configStopValue(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/configStopValue"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"
                               
    def configDegreeValue(self, value):
        try:
            html = urllib2.urlopen("http://"+self.IP+":8888/configDegreeValue"+self.formatString(value), timeout=TIMEOUT_VALUE)
            html = html.read().decode()
            _global_.robots_manager["ID::00" + self.ID]["battery"] = html
        except urllib2.URLError, e:
            print "Problem communicating with robot:"
            print e
        except socket.timeout:
            print "Socket timed out!"

    def run_plan(self, plan, robots):
        robots["ID::00" + self.ID]["running_plan"] = True
        for method in plan:
            if type(method) == str:
                getattr(self, method)()
            else:
                getattr(self, method[0])(method[1])
        print "Plan for ID:00" + str(self.ID) + " finished!"
        robots["ID::00" + self.ID]["running_plan"] = False

class Server():

    def __init__(self, host=None):
        self.robots = []
        if host is None:
            host = socket.gethostbyname(socket.gethostname()).split('.')
            self.host = host[0]+'.'+host[1]+'.'+host[2]
        else:
            self.host = host

    def scan(self, robotsAvailable):

        robots = []
        cache = register.ReadFile()
        ips = cache.getContentNoDupLn(CACHE_ADDRESS)
        i = 0
        q = 0

        while(i<=len(ips)-1):
            try:
                print "Try to get http://"+ips[i]+":8888/getid"
                html = urllib2.urlopen("http://"+ips[i]+":8888/getid", timeout=1)
                html = html.read().decode()
                print html
                html = html.split('-')
                robot = SendCommand(html[0],html[1])
                self.robots.append(robot)
                cache = register.WriteFile(CACHE_ADDRESS)
                cache.println(html[1])
                q = q+1

                if(q==robotsAvailable):
                    print "Robot found on cache"
                    return

            except urllib2.URLError:
                pass

            i = i+1
        i = 1

        while(i<=244):
            try:
                print "Try to get http://"+self.host+"."+str(i)+":8888/getid"
                html = urllib2.urlopen("http://"+self.host+"."+str(i)+":8888/getid", timeout=0.5)
            except urllib2.URLError:
                pass
            i = i+1
        i=1
        q = 0

        while(i<=244):
            try:
                print "Try to get http://"+self.host+"."+str(i)+":8888/getid"
                html = urllib2.urlopen("http://"+self.host+"."+str(i)+":8888/getid", timeout=0.5)
                html = html.read().decode()
                print html
                html = html.split('-')
                robot = SendCommand(html[0],html[1])
                self.robots.append(robot)
                cache = register.WriteFile(CACHE_ADDRESS)
                cache.println(html[1])
                q = q+1
                if(q==robotsAvailable):
                    break
            except urllib2.URLError:
                pass
            i = i+1

    def robotsOnline(self):
        return len(self.robots)

    def getRobot(self, code): 
        tam = len(self.robots)
        i = 0
        while(i<tam):
            if(self.robots[i].ID==code):
                return self.robots[i]
            i=i+1
