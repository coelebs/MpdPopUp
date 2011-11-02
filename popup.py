#!/usr/bin/python2
import pynotify
from mpd import MPDClient
from select import select
import urllib
import json
import os.path
import pprint

HOST = 'localhost'
PORT = '6600'

class SongNotify:
    def __init__(self):
        pynotify.init("mpd-notify")

    def newSong(self, song):
        hello = pynotify.Notification(song.title,
                song.title + " by " + song.artist + " from album " + song.album, 
                song.icon)
        hello.show()

LASTFMAPIKEY = "40887e583290b0d8932e3c872ac7aae5"

class Song:
    def __init__(self, song_dict):
        self.id = song_dict["id"]
        self.album = song_dict["album"]
        self.artist = song_dict["artist"]
        self.title = song_dict["title"]

        self.icon = None
        
        #if 'musicbrainz_trackid' in song_dict:
            #self.mbid = song_dict["musicbrainz_trackid"]
        #else:
        self.mbid = None

        self.fetch_lastfm()

    def fetch_lastfm(self):
        url = "http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&format=json"
        if self.mbid:
            url += "&mbid=%s" % self.mbid
        else:
            url += "&artist=%s&track=%s" % (self.artist, self.title)

        response = urllib.urlopen(url)
        song_dict = json.loads(response.read())["track"]
        self.albumid = song_dict["album"]["mbid"]
        self.icon = self.fetch_albumart(song_dict["album"]["image"][0]["#text"])
        
    def fetch_albumart(self, location):
        file_location = "/tmp/" + self.album
        if not os.path.isfile(file_location):
            response = urllib.urlopen(location)
            
            file_obj = open(file_location, "w")
            file_obj.write(response.read())
            file_obj.close()
        
        return file_location

class MpdWatcher:
    def __init__(self, host, port):
        self.client = MPDClient()

        try:
            self.client.connect(HOST, PORT)
        except SocketError:
            print("Failed to connect to MPD, exiting")
            sys.exit(1)
        self.notify = SongNotify()
        
        self.song = None
        self.updateSong(self.client.currentsong())

    def watch(self):
        while True:
            self.client.send_idle()
            select([self.client], [], [])
            changed = self.client.fetch_idle()
            if 'player' in changed:
                self.updateSong(self.client.currentsong())

    def updateSong(self, song):
        if not 'id' in song:
            return

        if self.song and song['id'] == self.song.id:
            return

        self.song = Song(song)
        
        if self.client.status()['state'] == 'play': 
            self.notify.newSong(self.song)
        else:
            print(self.client.status()['state'])

def test():
    client = MPDClient()
    notify = SongNotify()

    watch = MpdWatcher(HOST, PORT)
    watch.watch()

if __name__ == '__main__':
    test()
