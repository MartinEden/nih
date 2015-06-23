import pygst
pygst.require("0.10")
import gst
from enum import Enum
import threading
import gobject
from sys import stderr
from os.path import abspath

import logging
logger = logging.getLogger(__name__)

def logdebug(msg):
    logger.debug(msg)

class Status(Enum):
    idle = 1
    playing = 2
    paused = 3

class StateFailException(Exception):
    pass

class Player:
    def __init__(self, debug = False):
        self.debug = debug
        self.newPlayer()
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)
        self.status = Status.idle

        self.state_lock = threading.Condition()
        self.waiting_for_state_update = False

    def newPlayer(self):
        self._player = gst.element_factory_make("playbin", "player")

    def __del__(self):
        with self.state_lock:
            while self.waiting_for_state_update:
                if self.debug:
                    logdebug("waiting for update before deletion")
                self.state_lock.wait()

    def message_handler(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            if self.debug:
                logdebug("end of stream")
            self.next_track()
        
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            if err.domain == gst.STREAM_ERROR and err.code == gst.STREAM_ERROR_CODEC_NOT_FOUND and debug.find("gstplaybin")!=-1:
                if self.debug:
                    logdebug("Invalid track, skipping " + message)
            elif self.debug:
                logdebug("error: %s"%err)#, err.code, err.domain, err.message)
        
        elif t == gst.MESSAGE_STATE_CHANGED:
            if message.src == self._player:
                if self.debug:
                    logdebug("message from player")
                old, new, pending = message.parse_state_changed()
                if self.debug:
                    logdebug("state change %s %s %s"%(old, new, pending))
                if pending == gst.STATE_VOID_PENDING:
                    with self.state_lock:
                        self._set_internal_state(new)
                        if self.waiting_for_state_update:
                            self.waiting_for_state_update = False
                            self.state_lock.notifyAll()
        elif t == gst.MESSAGE_STREAM_STATUS:
            logdebug("stream status %s" % message)
        else:
            logger.info("unhandled message %s" % t)

        return gst.BUS_PASS

    def next_track(self):
        logdebug("next track")

    def elapsed(self):
        if self.status == Status.idle:
            return None
        else:
            (change, current, pending) = self._player.get_state()
            if self.debug:
                logdebug("state", change, current, pending)
            if current != gst.STATE_NULL:
                elapsed, format = self._player.query_position(gst.Format(gst.FORMAT_TIME), None)
                return elapsed / gst.SECOND
            else:
                if self.debug:
                    logdebug("bad state %s" % current)
                return None

    def _set_internal_state(self,state):
        if self.debug:
            logdebug("set internal state for %s"%state)
        if state == gst.STATE_NULL:
            self.status = Status.idle
        elif state == gst.STATE_PAUSED:
            self.status = Status.paused
        elif state == gst.STATE_PLAYING:
            self.status = Status.playing
        else:
            raise Exception, state

    def _set_state(self, state):
        with self.state_lock:
            while self.waiting_for_state_update:
                if self.debug:
                    logdebug("waiting for update")
                self.state_lock.wait()
            if self.debug:
                logdebug("got update")
        
        (info, current, _) = self._player.get_state()
        if current == gst.STATE_NULL and state == gst.STATE_PAUSED:
            if self.debug:
                logdebug("Can't pause")
        else:
            with self.state_lock:
                kind = self._player.set_state(state)
                if self.debug:
                    logdebug("set state result %s %s"%(state, kind))
                if kind == gst.STATE_CHANGE_ASYNC:
                    self.waiting_for_state_update = True
                elif kind == gst.STATE_CHANGE_SUCCESS:
                    self._set_internal_state(state)
                elif kind == gst.STATE_CHANGE_FAILURE:
                    raise StateFailException
                else:
                    raise Exception, kind
        
        # gstreamer appears to be partially quantum. measuring state changes results...
        (info, _, _) = self._player.get_state()
        if info == gst.STATE_CHANGE_FAILURE:
            raise StateFailException

    def stop(self):
        if self.debug:
            logdebug("state: stopping")
            logdebug(self._player.get_state())
        self._set_state(gst.STATE_NULL)
        if self.debug:
            logdebug(self._player.get_state())

    def pause(self):
        if self.debug:
            logdebug("state: pausing")
            logdebug(self._player.get_state())
        self._set_state(gst.STATE_PAUSED)
        if self.debug:
            logdebug(self._player.get_state())

    def unpause(self):
        if self.debug:
            logdebug("state: pausing")
            logdebug(self._player.get_state())
        self._set_state(gst.STATE_PLAYING)
        if self.debug:
            logdebug(self._player.get_state())

    def play(self, path):
        if self.debug:
            logdebug("state: playing")
            logdebug(self._player.get_state())
        path = abspath(path)
        try:
            self._player.set_property("uri", "file://"+path)
            if self.debug:
                logdebug("state: playing (set uri)")
            self._set_state(gst.STATE_PLAYING)
            if self.debug:
                logdebug("now playing", path)
        except StateFailException:
            self._player.set_state(gst.STATE_NULL)
            self.waiting_for_state_update = False
            self.newPlayer()
            self.next_track()

        if self.debug:
            logdebug(self._player.get_state())

