from jsonrpc import jsonrpc_method
from globals import site
from django.conf import settings

from alsaaudio import Mixer, ALSAAudioError

volume_who = ""
volume_direction = ""

def get_mixer():
    if settings.MIXER_CONTROL:
        return Mixer(control=settings.MIXER_CONTROL)
    else:
        return Mixer()


def volume():
    try:
        volume = get_mixer().getvolume()[0]
    except ALSAAudioError:
        volume = 'Error'
    return {"volume":volume, "who":volume_who, "direction": volume_direction}

@jsonrpc_method('get_volume', site=site)
def get_volume(request):
    return volume()

@jsonrpc_method('set_volume', site=site)
def set_volume(request, username, value):
    global volume_who, volume_direction
    m = get_mixer()
    if value > m.getvolume()[0]:
        volume_direction = "up"
        volume_who = username
    elif value < m.getvolume()[0]:
        volume_direction = "down"
    else:
        return volume() # no change, quit
    
    volume_who = username
    m.setvolume(value)
    return volume()
