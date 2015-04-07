from jsonrpc import jsonrpc_method
from globals import site

from helpers import metadata
from jukebox.models import ChatItem
from time import mktime

def chat_history(request, limit):
    ret = []
    for item in ChatItem.view("jukebox/all_chatitems", limit = 10):
        msg = { 
            "when": mktime(item.when.timetuple()),
            "what": item.what
        }
        if item.who:
            msg["who"] = item.who

        player_actions = [
            'skip',
            'play',
            'pause',
            'resume',
        ]

        if item.what in player_actions:
            msg["track"] = {"url":item.info.url}
            msg["info"] = metadata(item.info)
        elif item.what == "failed":
            msg["error"] = "Failed to download %s"%item.info.url
        else:
            msg["message"] = item.message
        ret.append(msg)
    return ret

@jsonrpc_method('chat', site=site)
def chat(request, username, text):
    ChatItem(what="says", message=text, who=username).save()

@jsonrpc_method('get_history', site=site)
def get_history(request, limit):
    return chat_history(request, limit)
