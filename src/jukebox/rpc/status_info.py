from jukebox.models import QueueItem
from simple_player import Status
from jukebox.downloader import downloader
from globals import player
from helpers import metadata

def serialize_queue(queue):
    timeToStart = 0
    items = []
    current = queue[0]
    for q in queue:
        item = {
            "id": q.id,
            "url": q.what.url,
            "username": q.who,
            "index": q.index,
            "timeToStart": timeToStart
        }
        if q.what.got_metadata and timeToStart != None:
            timeToStart += q.what.trackLength
            if q == current and player.elapsed():
                timeToStart -= player.elapsed()
        else:
            timeToStart = None
        items.append(item)
    return items

def get_items():
    objects = QueueItem.objects.all()
    if objects.count():
        items = serialize_queue(objects)
        itemsMeta = [metadata(x.what) for x in objects]
        return items, itemsMeta
    else:
        return [None], [None]

def get_state():    
    current = QueueItem.current()
    if current!=None and current.what in downloader.downloads():
        return "caching"
    else:
        return player.status.name()

def status_info(request):
    items, itemsMeta = get_items()
    first = (items[0], itemsMeta[0])
    return {
        "status": get_state(),
        "entry":first[0],
        "info": first[1],
        "queue": items[1:],
        "queueInfo": itemsMeta[1:],
        "paused": player.status != Status.playing,
        "elapsedTime": player.elapsed(),
        "downloads": [x.url for x in downloader.downloads()]
    }
