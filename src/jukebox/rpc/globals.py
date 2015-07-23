from jsonrpc.site import JSONRPCSite
site = JSONRPCSite()

import jukebox.audioscrobbler
from django.conf import settings
from jukebox.models import QueueItem, ChatItem
from simple_player import Player, Status
from helpers import reindex_queue
from jukebox.cache import cached
from time import strftime, gmtime
import logging

logger = logging.getLogger(__name__)

def make_audioscrobbler():
    if settings.LASTFM_ENABLED:
        audioscrobbler.enc = "utf8"
        return audioscrobbler.AudioScrobblerPost(username=settings.LASTFM_USER, password=settings.LASTFM_PASSWORD, verbose=True)
    else:
        def do_nothing(**kwargs):
            pass
        return do_nothing

def next_track():
    logger.debug("Next track. Count %d, Status %s", QueueItem.objects.count(), player.status)
    if QueueItem.objects.all().count() > 0:
        QueueItem.current().delete() # remove current first item from queue
        player.stop()
        reindex_queue()
    if QueueItem.objects.all().count()>0:
        play_current(player)
    elif player.status != Status.idle:
        player.stop()

def play_current(player):
    toplay = QueueItem.current()
    f = cached(toplay.what)
    logging.debug("toplay %s", f)
    if f != None:
        player.play(f)
        song = toplay.what
        track = dict(artist_name=song.artist,
                 song_title=song.title,
                 length=int(song.trackLength),
                 date_played=strftime("%Y-%m-%d %H:%M:%S", gmtime()), 
                 album=song.album,
                 mbid=""
                )
        logging.debug("track %s", track)
        post(**track)
        ChatItem(what="play", info=song, who=toplay.who).save()
    else:
        player.stop()
        ChatItem(what="stop", who=None).save()

post = make_audioscrobbler()
player = Player()
player.next_track = next_track
