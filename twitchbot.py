import requests
import subprocess
import json
import sys
import threading
import time
from Queue import Queue

numberOfViewers = int(100)
builderThreads = int(10)
startTime = time.time()
numberOfSockets = 0
concurrent = 25
urls = []
urlsUsed = []


def getURL():  # Get tokens
    output = subprocess.Popen(["livestreamer", "twitch.tv/zappingoombaz", "-j"], stdout=subprocess.PIPE).communicate()[0]
    return json.loads(output)['streams']['worst']['url']  # Parse json and return the URL parameter

def build():  # Builds a set of tokens, aka viewers
    global numberOfSockets
    global numberOfViewers
    while True:
        if numberOfSockets < numberOfViewers:
            numberOfSockets += 1
            print "Building viewers " + str(numberOfSockets) + "/" + str(numberOfViewers)
            urls.append(getURL())


def view():  # Opens connections to send views
    global numberOfSockets
    while True:
        url = q.get()
        requests.head(url)
        if (url in urlsUsed):
            urls.remove(url)
            urlsUsed.remove(url)
            numberOfSockets -= 1
        else:
            urlsUsed.append(url)
        q.task_done()


if __name__ == '__main__':
    for i in range(0, builderThreads):
        threading.Thread(target=build).start()
    print 'here1'
    while True:
        while (numberOfViewers != numberOfSockets):  # Wait until sockets are built
            time.sleep(1)
        print 'here2'
        q = Queue(concurrent * 2)
        for i in range(concurrent):
            try:
                t = threading.Thread(target=view)
                t.daemon = True
                t.start()
                print 'here3'
            except:
                print 'thread error'
        try:
            for url in urls:
                print url
                q.put(url.strip())
                q.join()
        except KeyboardInterrupt:
            sys.exit(1)
