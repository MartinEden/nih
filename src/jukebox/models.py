from hashlib import md5
from django.core.signals import request_started
from utils import runStartupTasks
from couchdbkit.ext.django.schema import *
from datetime import datetime

class WebPath(Document):
    url = StringProperty()
    
    def __unicode__(self):
        if self.checked:
            return "Checked url: %s"%self.url
        elif self.failed:
            return "Failed url: %s"%self.url
        else:
            return "Unchecked url: %s"%self.url

    checked = BooleanProperty(default=False)
    failed = BooleanProperty(default=False)

    root = StringProperty()

    @staticmethod
    def add_root(url):
        wp = WebPath(url = url, root = None)
        wp.save()
        print "saved root"
        return wp

    def add_child(self, url):
        if self.root == None: # assume we're root
            wp = WebPath(root = self, url = url)
        else:
            wp = WebPath(root = self.root, url = url)
        wp.save()
        return wp

    @staticmethod
    def get_root_nodes():
        return WebPath.objects.exclude(root__isnull =False)

class MusicFile(Document):
    url = StringProperty()
    parent = StringProperty(WebPath)

    def __unicode__(self):
        if self.got_metadata:
            return " - ".join([x for x in (self.artist, self.album, self.title) if x!=""])
        else:
            return "Unchecked url: %s"%self.url

    failed = BooleanProperty(default=False)
    got_metadata = BooleanProperty(default=False)
    artist = StringProperty()
    album = StringProperty()
    title = StringProperty()
    trackLength = IntegerProperty()
    trackNumber = StringProperty()

    def hash(self):
        return md5(self.url).hexdigest()

class DateTimePropertyWithNow(DateTimeProperty):
    def default_value(self):
        return datetime.now()

class ChatItem(Document):
    what = StringProperty()
    when = DateTimePropertyWithNow(required = True)
    who = StringProperty()

    info = StringProperty()
    message = StringProperty()

    class Meta:
        ordering = ["-when", "-id"]

    def __unicode__(self):
        ret = "<Chat: %s, %s, %s, "%(self.what, self.when, self.who)
        if self.what == "skip":
            ret += str(self.info)
        else:
            ret += self.message
        return ret + ">"

class QueueItem(Document):
    who = StringProperty()
    what = StringProperty('MusicFile')
    index = FloatProperty()

    @staticmethod
    def current():
        items = QueueItem.view("jukebox/all_queueitems")[:1]
        if len(items) == 0:
            return None
        else:
            return items[0]

    def __unicode__(self):
        return "<Music item %s>"%str(self.what)
    
    class Meta:
        ordering = ["index"]

request_started.connect(runStartupTasks)

