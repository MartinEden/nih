from player import Player
import unittest
import threading
import gobject

class Looper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        gobject.threads_init()

    def run(self):
        self.loop = gobject.MainLoop()
        self.loop.run()

    def quit(self):
        self.loop.quit()

class TestPlayer(unittest.TestCase):
    fname = "../jukebox/static/silent-3mins.mp3"
    loop = None
    player = Player(debug=True)

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        if TestPlayer.loop == None:
            TestPlayer.loop = Looper()
            TestPlayer.loop.setDaemon(True)
            TestPlayer.loop.start()

    def __del__(self):
        if TestPlayer.loop != None:
            TestPlayer.loop.quit()
            TestPlayer.loop = None

    def testPlaying(self):
        self.player.play(self.fname)

    def testMultiplePlaying(self):
        self.player.play(self.fname)
        self.player.play(self.fname)
    
    def testStopStart(self):
        self.player.play(self.fname)
        self.player.stop()
        self.player.play(self.fname)
    
    def testQueue(self):
        items = [self.fname]*3

        f = self.fname
        while True:
            if f != None:
                self.player.pause()
                self.player.play(f)
            else:
                self.player.stop()

            if f == None:
                break
            elif len(items)>0:
                f = items[0]
                items = items[1:]
            else:
                f = None


if __name__ == "__main__":
    unittest.main()
