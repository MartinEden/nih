from player import Player
from sys import argv
import threading
import gobject
from time import sleep

class Looper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        gobject.threads_init()

    def run(self):
        self.loop = gobject.MainLoop()
        self.loop.run()

    def quit(self):
        self.loop.quit()

loop = Looper()
loop.setDaemon(True)
loop.start()

player = Player()
player.play(argv[1])
sleep(1)
