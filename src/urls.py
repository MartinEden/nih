from django.conf.urls import url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings

from utils import site_path
import jukebox.jsonfuncs
import jukebox.configfuncs

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_path('jukebox/static'), 'show_indexes': True}),
    url(r'^cache/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_path(settings.CACHE_FOLDER), 'show_indexes': True}),
    url(r'^spider$', 'jukebox.views.spider'),
    url(r'^config$', 'jukebox.views.config'),
    url(r'^$', 'jukebox.views.index'),
    url(r'^oldui$', 'jukebox.views.oldui'),
    url(r'^rpc/jukebox/browse$', 'jsonrpc.views.browse', name="jsonrpc_browser", kwargs={"site":jukebox.jsonfuncs.site}),
    url(r'^rpc/jukebox', jukebox.jsonfuncs.site.dispatch, name="jsonrpc_mountpoint"),
    url(r'^rpc/config', jukebox.configfuncs.site.dispatch, name="jsonrpc_mountpoint")
]
print "opened urls.py"
print jukebox.jsonfuncs.site

#One time startup
#http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only

from jukebox.models import ChatItem
ChatItem(what="start", message="Server started", who=None).save()
