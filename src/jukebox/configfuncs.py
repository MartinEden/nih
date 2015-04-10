from jsonrpc import jsonrpc_method
from jsonrpc.site import JSONRPCSite
from models import *
from utils import urlopen
from time import time

site = JSONRPCSite()

@jsonrpc_method("all_roots", site=site)
def all_roots(request):
    ret = []
    items = WebPath.view("jukebox/root_counts", wrap_doc=False, group=True)
    print "counts", items
    for root in items:
        ret.append({"url":root['key'], "count":root['value']})
    return sorted(ret, key=lambda x: x['url'])

@jsonrpc_method("current_rescans", site=site)
def current_rescans(request):
    ret = []
    for root in WebPath.get_root_nodes():
        if len([x for x in WebPath.to_spider() if hasattr(x, "url") and x.url == root.url]) > 0:
            ret.append(root.url)
    return sorted(ret)

@jsonrpc_method("rescan_root", site=site)
def rescan_root(request, root):
    result = "success"
    for x in WebPath.get_root_nodes():
        if x.url == root:
            SpideringPath(url = x.url).save()
            break
    else:
        try:
            urlopen(root)
            wp = WebPath(url = root, root = None)
            wp.save()
            SpideringPath(url = root).save()
        except Exception, e:
            print "don't like", root, e
            print request.META
            result = "failure"
        
    return {
        "result": result,
        "root": root,
        "current_rescans": current_rescans(request)
    }
        
@jsonrpc_method("remove_root", site=site)
def remove_root(request, root):
    for x in WebPath.get_root_nodes():
        if x.url == root:
            start = time()
            print "deleting", root, x
            MusicFile.objects.filter(parent__root = x).delete()
            WebPath.objects.filter(root = x).delete()
            x.delete()
            print "deleted", time()-start
            break
    
    return all_roots(request)
    
