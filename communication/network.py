from urllib2 import Request
import urllib2
import socket
import register

CACHE_ADDRESS = "communication/cache.txt"

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
        html = urllib2.urlopen("http://"+self.IP+":8888/rotateLeft"+self.formatString(value))
        html = html.read().decode()
        print html

    def rotateRight(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/rotateRight"+self.formatString(value))
        html = html.read().decode()
        print html

    def moveForward(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/moveForward"+self.formatString(value))
        html = html.read().decode()
        print html

    def moveBack(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/moveBack"+self.formatString(value))
        html = html.read().decode()
        print html

    def invert(self):
        html = urllib2.urlopen("http://"+self.IP+":8888/invert")
        html = html.read().decode()
        print html
                               
    def shiftUp(self):
        html = urllib2.urlopen("http://"+self.IP+":8888/shiftUp")
        html = html.read().decode()
        print html
                               
    def shiftDown(self):
        html = urllib2.urlopen("http://"+self.IP+":8888/shiftDown")
        html = html.read().decode()
        print html
                               
    def configDelay(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/configDelay"+self.formatString(value))
        html = html.read().decode()
        print html
                               
    def configStopValue(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/configStopValue"+self.formatString(value))
        html = html.read().decode()
        print html
                               
    def configDegreeValue(self, value):
        html = urllib2.urlopen("http://"+self.IP+":8888/configDegreeValue"+self.formatString(value))
        html = html.read().decode()
        print html

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
                html = urllib2.urlopen("http://"+ips[i]+":8888/getid", timeout=5)
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
                html = urllib2.urlopen("http://"+self.host+"."+str(i)+":8888/getid", timeout=0.1)
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
