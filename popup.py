#!/usr/bin/python2
import pynotify
from mpd import MPDClient
from select import select

HOST = 'localhost'
PORT = '6600'

class SongNotify:
    def __init__(self):
        pynotify.init("mpd-notify")

    def newSong(self, song):
        print("test")
        hello = pynotify.Notification(song['title'],
                song['title'] + " by " + song['artist'] + " from album " + song['album'], 
                "/home/vincent/yolanthe_1.jpg")
        hello.show()


class MpdWatcher:
    def __init__(self, host, port):
        self.client = MPDClient()

        try:
            self.client.connect(HOST, PORT)
        except SocketError:
            print("Failed to connect to MPD, exiting")
            sys.exit(1)
        self.notify = SongNotify()
        
        self.song = {'id': -1}
        self.updateSong(self.client.currentsong())

    def watch(self):
        while True:
            self.client.send_idle()
            select([self.client], [], [])
            changed = self.client.fetch_idle()
            if 'player' in changed:
                self.updateSong(self.client.currentsong())

    def updateSong(self, song):
        if 'id' not in song:
            return

        if song['id'] == self.song['id']:
            return

        self.song = song
        
        if self.client.status()['state'] == 'play': 
            print("test1")
            self.notify.newSong(song)
        else:
            print(self.client.status()['state'])

if __name__ == '__main__':
    client = MPDClient()
    notify = SongNotify()

    watch = MpdWatcher(HOST, PORT)
    watch.watch()
