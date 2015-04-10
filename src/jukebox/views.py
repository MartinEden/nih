from django_genshi import render_to_response
from django.conf import settings
#from spider import spider
from models import *

def _index_data(request):
    data = { 
        "lastfm_name": settings.LASTFM_USER,
        "repo_url": settings.REPO_URL,
    }
    data["has_lastfm"] = settings.LASTFM_ENABLED
    username = request.GET.get('username', None)
    if username:
        data["username"] = username
    data["has_username"] = "username" in data
    return data

def index(request):    
    return render_to_response("index.xml", _index_data(request))

def oldui(request):
    return render_to_response("oldui.xml", _index_data(request))  

def spider(request):
    return render_to_response("spider.xml", {"spider": spider})

def config(request):
    return render_to_response("config.xml", {"roots": WebPath.get_root_nodes()})
