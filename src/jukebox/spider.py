from models import WebPath, MusicFile
from BeautifulSoup import BeautifulSoup
from utils import urlopen, URLError, BackgroundTask, registerStartupTask
from urlparse import urljoin
from os.path import splitext
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

known_extensions = [".mp3", ".ogg", ".flac", ".wma", ".m4a"]

class Spider(BackgroundTask):
    def startup(self):
        for x in WebPath.objects.filter(checked=False, failed=False):
            self.add(x)

    def processItem(self, current):
        try:
            test = current.root
        except WebPath.DoesNotExist:
            logger.debug("skipping, as no more root!")
            current.delete()
            return

        try:
            page = urlopen(current.url)
        except URLError:
            logger.debug("fail", current.url)
            current.failed = True
            current.save()
            return

        try:
            url = page.geturl()
            soup = BeautifulSoup(page)
        
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
                    if WebPath.objects.filter(url=resolved).count() == 0:
                        child = current.add_child(url=resolved)
                        self.add(child)
                else: # file?
                    (_, ext) = splitext(resolved)
                    ext = ext.lower()
                    if ext in known_extensions:
                        if MusicFile.objects.filter(url=resolved).count() == 0:
                            mf = MusicFile(parent=current, url = resolved)
                            mf.save()
                    else:
                        logger.debug("can't handle %s %s %s", resolved, ext, len(ext))

            current.checked = True
            current.save()
        except ObjectDoesNotExist:
            # we got deleted
            current.delete()

if settings.TESTING:
    spider = Spider()
    spider.setDaemon(True)
else:
    spider = registerStartupTask(Spider)
