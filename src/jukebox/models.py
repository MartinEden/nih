from __future__ import absolute_import
from hashlib import md5
from django.core.signals import request_started
from utils import runStartupTasks
from couchdbkit.ext.django.schema import *
from datetime import datetime

class URLIdDocument(Document):
    def __setattr__(self, key, value):
        if key == "url":
            self.__setattr__("_id", value)
        else:
            Document.__setattr__(self, key, value)

    def __getattr__(self, key):
        if key == "url":
            return self._id
        else:
            return Document.__getattr__(self, key)

    def __str__(self):
        return "<%s: %s>" %(self.__class__, self.url)

class WebPath(URLIdDocument):
    def __unicode__(self):
        if self.checked:
            return "Checked url: %s"%self.url
        elif self.failed:
            return "Failed url: %s"%self.url
        else:
            return "Unchecked url: %s"%self.url

    checked = BooleanProperty(default=False)
    failed = BooleanProperty(default=False)

    parent = StringProperty()
    root = StringProperty()

    def get_root(self):
        if self.root == None:
            return self.url
        else:
            return self.root

    @staticmethod
    def to_spider():
        return WebPath.view("jukebox/to_spider", include_docs = True, classes={None: Document, 'WebPath': WebPath})

    def add_child(self, url):
        wp = WebPath(root = self.get_root(), url = url)
        wp.save()
        return wp

    @staticmethod
    def get_root_nodes():
        return WebPath.view("jukebox/root_nodes")

class SpideringPath(Document):
    url = StringProperty()

class MusicFile(URLIdDocument):
    parent = StringProperty(WebPath)
    root = StringProperty()

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

