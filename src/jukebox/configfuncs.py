from jsonrpc import jsonrpc_method
from jsonrpc.site import JSONRPCSite
from models import *
from spider import spider
from utils import urlopen
from time import time
import logging

logger = logging.getLogger(__name__)
site = JSONRPCSite()

@jsonrpc_method("all_roots", site=site)
def all_roots(request):
    ret = []
    for root in WebPath.get_root_nodes():
        ret.append({"url":root.url, "count":MusicFile.objects.filter(url__startswith=root.url).count()})
    return sorted(ret, key=lambda x: x['url'])

@jsonrpc_method("current_rescans", site=site)
def current_rescans(request):
    ret = []
    for root in WebPath.get_root_nodes():
        if WebPath.objects.filter(checked = False, failed=False,url__startswith=root.url).count()>0:
            ret.append(root.url)
    return sorted(ret)

@jsonrpc_method("rescan_root", site=site)
def rescan_root(request, root):
    result = "success"
    for x in WebPath.get_root_nodes():
        if x.url == root:
            spider.pause()
            x.delete()
            spider.add(WebPath.add_root(root))
            spider.unpause()
            break
    else:
        try:
            urlopen(root)
            spider.add(WebPath.add_root(url=root))
        except Exception, e:
            logger.debug("don't like %s %s %s", root, e, request.META)
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
            spider.pause()
            start = time()
            logger.debug("deleting %s %s", root, x)
            MusicFile.objects.filter(parent__root = x).delete()
            WebPath.objects.filter(root = x).delete()
            x.delete()
            logger.debug("deleted %s", time()-start)
            spider.unpause()
            break
    
    return all_roots(request)
    
