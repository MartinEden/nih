from os.path import join, dirname
import urllib2
from threading import Thread, Lock, Condition
import logging
logger = logging.getLogger(__name__)

client = None
URLError = urllib2.URLError

def site_path(path):
    return join(dirname(__file__), path)

class FakeURLObject:
    def __init__(self, backing, url):
        self.backing = backing
        self.url = url

    def geturl(self):
        return self.url

    def read(self):
        return self.backing.content

def urlopen(url):
    try:
        return urllib2.urlopen(url)
    except URLError:
        global client
        if client == None:
            from django.test.client import Client
            client = Client()
        local = "http://localhost"
        if url.find(local) != -1: # assume local server attempt, so try test client
            path = url[len(local):]
            obj = client.get(path)
            if obj.status_code != 200:
                raise
            return FakeURLObject(obj, url)
        else:
            raise

class BackgroundTask(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.paused = False
        self.queue = []
        self.queueCondition = Condition()

    def todo(self):
        with self.queueCondition:
            return list(self.queue)

    def run(self):
        self.startup()
        while True:
            with self.queueCondition:
                while True:
                    if not self.paused and len(self.queue)>0:
                        item = self.queue[0] # don't remove it yet though (still needs to be marked as "caching")
                        break
                    else:
                        logger.debug("waiting %s"% self)
                        self.queueCondition.wait()

            self.processItem(item)

            with self.queueCondition:
                assert len(self.queue)>0
                assert self.queue[0] == item, (item, self.queue)
                self.queue = self.queue[1:]
            
            self.postProcessItem(item)    

    def add(self, item):
        with self.queueCondition:
            self.queue.append(item)
            logger.debug("got item for %s %s %s" %(self, item, self.paused))
            if not self.paused:
                self.queueCondition.notify()

    def startup(self):
        pass
    
    def processItem(self):
        raise Exception, "Subclasses must implement processItem"

    def postProcessItem(self, item):
        pass

    # for testing purposes only. Make sure you call unpause if you're using pause!
    
    def pause(self):
        logger.debug("pausing %s" % self)
        self.paused = True

    def unpause(self):
        logger.debug("unpausing %s" % self)
        self.paused = False
        with self.queueCondition:
            self.queueCondition.notify()

startup_tasks = []
started = False
taskLock = Lock()

def registerStartupTask(kind):
    global startup_tasks, started, taskLock
    
    with taskLock:
        for item in startup_tasks:
            # can't use isinstance as we get nih.jukebox.* and jukebox.* ....
            if kind.__name__ == item.__class__.__name__:
                return item

        task = kind()
        task.setDaemon(True)

        startup_tasks.append(task)
        if started:
            task.start()
            logger.debug("already started %s %s" %(task, startup_tasks))
    return task

def runStartupTasks(sender, **kwargs):
    global startup_tasks, started, taskLock
    with taskLock:
        if started:
            return
        started = True
        for t in startup_tasks:
            t.start()
