from jsonrpc import jsonrpc_method
from globals import site

from jukebox.cache import cached
from jukebox.models import QueueItem, MusicFile
from status_info import status_info
from helpers import reindex_queue

import logging
logger = logging.getLogger(__name__)

@jsonrpc_method('enqueue', site=site)
def enqueue(request, username, tracks, atTop):
    logger.debug("enqueue: %s", tracks)
    for t in tracks:
        q = QueueItem(who = username, what = MusicFile.objects.get(url=t['url']))
        cached(q.what)
        try:
            if atTop:
                items = QueueItem.objects.all().order_by("index")
                if len(items)> 1:
                    q.index = (items[0].index+items[1].index)/2
                else:
                    q.index = items[0].index + 1 # only current item in queue
            else:
                q.index = QueueItem.objects.order_by("-index")[0].index + 1 # only current item in queue
        except IndexError: # nothing else in queue
            q.index = 0
        q.save()
    return status_info(request)

@jsonrpc_method('dequeue', site=site)
def dequeue(request, username, trackId):
    queue = list(QueueItem.objects.all())[1:]
    for item in queue:
        if item.id == trackId:
            item.delete()
    reindex_queue()
    return status_info(request)

@jsonrpc_method('clear_queue', site=site)
def clear_queue(request, username):
    queue = list(QueueItem.objects.all())[1:]
    for item in queue:
        item.delete()
    return status_info(request)

@jsonrpc_method('get_queue', site=site)
def get_queue(request):
    logger.debug("get_queue")
    return status_info(request)

@jsonrpc_method('reorder', site=site)
def reorder(request, trackId, new_position):
    queue = list(QueueItem.objects.all())[1:]
    length = len(queue)
    if new_position < 1:
        raise Exception("Cannot move items above position 1 in the queue")
    if new_position > length:
        new_position = length
    
    mover = QueueItem.objects.get(id=trackId)
    old_position = mover.index
    if old_position == 0:
        raise Exception("Cannot move the currently playing track")

    # Shuffle items that were previously below this item up to fill
    # the gap it left when it moved down
    if new_position > old_position: 
        for _, item in enumerate(queue):
            if item.index > old_position and item.index <= new_position:
                item.index -= 1
                item.save()

    # Shuffle items that were previously above this item down to fill
    # the gap it left when it moved up
    if new_position < old_position: 
        for _, item in enumerate(queue):
            if item.index >= new_position and item.index < old_position:
                item.index += 1
                item.save()

    mover.index = new_position
    mover.save()

    return status_info(request)
