from __future__ import absolute_import
from .models import WebPath, MusicFile, SpideringPath
from BeautifulSoup import BeautifulSoup
from utils import urlopen, URLError, BackgroundTask, registerStartupTask
from urlparse import urljoin
from os.path import splitext
from django.core.exceptions import ObjectDoesNotExist
from couchdbkit.exceptions import ResourceNotFound
from threading import Timer
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

known_extensions = [".mp3", ".ogg", ".flac", ".wma", ".m4a"]

class Spider(BackgroundTask):
    def startup(self):
        self.add_todo()

<<<<<<< HEAD
    def add_todo(self):
        with self.queueCondition:
            queued_urls = [x["key"] for x in self.queue]

            def row_wrapper(row):
                return row
=======
    def processItem(self, current):
        try:
            test = current.root
        except WebPath.DoesNotExist:
            logger.debug("skipping, as no more root!")
            current.delete()
            return
>>>>>>> master

            for x in WebPath.get_db().view("jukebox/to_spider", wrapper = row_wrapper):
                if x["key"] not in queued_urls:
                    print "adding", x["key"]
                    self.add(x)

        t = Timer(5, self.add_todo)
        t.start()

    def processItem(self, current):
        print "current", current
        url = current["key"]
        try:
            page = urlopen(url)
            wp = WebPath.get(url)
            wp.failed = False
            wp.save()
        except URLError:
            logger.debug("fail", current.url)
            try:
                wp = WebPath.get(url)
                wp.failed = True
                wp.save()
            except ResourceNotFound:
                print "Can't find the WebPath for %s" % url

            logger.debug("Deleting", current["id"], current["key"])
            SpideringPath.get(current["id"]).delete()
            return

        try:
            url = page.geturl()
            soup = BeautifulSoup(page)

            wp = WebPath.get(url)
            for link in soup.findAll("a"):
                try:
                    resolved = urljoin(url, link["href"])
                except KeyError:
                    logger.debug("skipping due to lack of href %s", link)
                    continue
                if len(resolved) < len(url): # up link, skip
                    logger.debug("skipping %s %s", resolved, url)
                    continue
                if resolved[-1] == "/": # directory
                    if WebPath.view("jukebox/all_webpaths", key = resolved).count() == 0:
                        child = wp.add_child(url=resolved)
                        self.add(child)
                else: # file?
                    (_, ext) = splitext(resolved)
                    ext = ext.lower()
                    if ext in known_extensions:
                        if MusicFile.view("jukebox/all_musicfiles", key = resolved).count() == 0:
                            mf = MusicFile(parent = wp.url, url = resolved, root = wp.get_root())
                            mf.save()
                    else:
                        logger.debug("can't handle %s %s %s", resolved, ext, len(ext))

        except ObjectDoesNotExist:
            # we got deleted
            current.delete()

if __name__ == "__main__":
    s = Spider()
    s.start()
    s.join()
#else:
#   spider = registerStartupTask(Spider)

#if settings.TESTING:
#    spider = Spider()
#    spider.setDaemon(True)
#else:
#    spider = registerStartupTask(Spider)
