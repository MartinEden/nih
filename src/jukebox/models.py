from django.db import models
from hashlib import md5
from django.core.signals import request_started
from utils import runStartupTasks
import logging
logger = logging.getLogger(__name__)

class WebPath(models.Model):
    url = models.TextField()
    
    def __unicode__(self):
        if self.checked:
            return "Checked url: %s"%self.url
        elif self.failed:
            return "Failed url: %s"%self.url
        else:
            return "Unchecked url: %s"%self.url

    checked = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)

    root = models.ForeignKey('self', null=True, blank=True)

    @staticmethod
    def add_root(url):
        wp = WebPath(url = url, root = None)
        wp.save()
        logger.debug("saved root")
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

class MusicFile(models.Model):
    url = models.TextField()
    parent = models.ForeignKey(WebPath)

    def __unicode__(self):
        if self.got_metadata:
            return " - ".join([x for x in (self.artist, self.album, self.title) if x!=""])
        else:
            return "Unchecked url: %s"%self.url

    failed = models.BooleanField(default=False)
    got_metadata = models.BooleanField(default=False)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    trackLength = models.IntegerField(blank=True, null=True)
    trackNumber = models.CharField(max_length=50)

    def hash(self):
        return md5(self.url).hexdigest()

class ChatItem(models.Model):
    what = models.CharField(max_length=200)
    when = models.DateTimeField(auto_now_add=True)
    who = models.CharField(max_length=200, null=True, blank=True)

    info = models.ForeignKey('MusicFile', null=True, blank=True)
    message = models.CharField(max_length=1024)

    class Meta:
        ordering = ["-when", "-id"]

    def __unicode__(self):
        ret = "<Chat: %s, %s, %s, "%(self.what, self.when, self.who)
        if self.what == "skip":
            ret += str(self.info)
        else:
            ret += self.message
        return ret + ">"

class QueueItem(models.Model):
    who = models.CharField(max_length=200)
    what = models.ForeignKey('MusicFile')
    index = models.FloatField()    

    @staticmethod
    def current():
        items = QueueItem.objects.all()[:1]
        if len(items) == 0:
            return None
        else:
            return items[0]

    def __unicode__(self):
        return "<Music item %s>"%str(self.what)
    
    class Meta:
        ordering = ["index"]

request_started.connect(runStartupTasks)

