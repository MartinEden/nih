from jsonrpc import jsonrpc_method
from globals import site, player, post, play_current

from jukebox.models import QueueItem, ChatItem
from simple_player import Status
from status_info import status_info
import logging

logger = logging.getLogger(__name__)

@jsonrpc_method('skip', site=site)
def skip(request, username):
    current = QueueItem.current()
    if current != None:
        ChatItem(what="skip", info = current.what, who=username).save()
        logger.debug("saved item %s", current.what)
        player.next_track()
    return status_info(request)

@jsonrpc_method('pause', site=site)
def pause(request, shouldPause, username):
    current = QueueItem.current()
    if not shouldPause:
        if player.status == Status.idle and QueueItem.objects.count()>0:
            from jukebox.cache import is_cached
            if is_cached(current.what):
                play_current(player)
        elif player.status == Status.paused:
            player.unpause()
            ChatItem(what="resume", info=current.what, who=username).save()
    else:
        if player.status == Status.playing:
            player.pause()
            ChatItem(what="pause", info=current.what, who=username).save()

    return status_info(request)

def get_status():
    return player.status
