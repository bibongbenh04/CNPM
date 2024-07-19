import webbrowser, json
import pygame

class Song:
    def __init__(self, name_song, main_artist_song, composer_song, lyricist_song,  url_song, id_song = None):
        self.id_song = id_song
        self.name_song = name_song
        self.main_artist_song = main_artist_song
        self.composer_song = composer_song
        self.lyricist_song = lyricist_song
        self.url_song = url_song
        
    def __eq__(self, other):
        if isinstance(other, Song):
            return self.name_song == other.name_song or self.url_song == other.url_song
    def getId(self):
        return self.id_song
    def getName(self):
        return self.name_song
    def getArtist(self):
        return self.main_artist_song
    def getComposer(self):
        return self.composer_song
    def getUrl(self):
        return self.url_song
    def getLyricist(self):
        return self.lyricist_song
    def show(self):
        return f'({self.id_song},"Name:", {self.name_song},"Aritist:", {self.main_artist_song},"Composer:", {self.composer_song},"Lyrics:", {self.lyricist_song},"Url:",{self.url_song})'


class ListSong:
    def __init__(self):
        self.list = []
        self.loadAllSongs()
    def getAllSongs(self):
        return self.list
    def add_song(self, song)->bool:
        if not self.checkSong(song):
            self.list.append(song)
            self.saveAllSongs()
            return True
        else:
            return False
    def show_all_song(self):
        for i in self.list:
            i.show()
    def loadAllSongs(self):
        try:
            with open("data/songs.json", "r") as file:
                jsonfile = json.load(file)
                for mov in jsonfile:
                    song = Song(mov["name_song"],mov["main_artist_song"],mov["composer_song"],mov["lyricist_song"],mov["url_song"],mov["id_song"])
                    self.add_song(song)
        except FileNotFoundError:
            print("The file 'data/songs.json' was not found.")
        except json.JSONDecodeError:
            print("The file 'data/songs.json' does not contain valid JSON data.")
    def checkSong(self, song):
        return song in self.list
    def saveAllSongs(self):
        jsonfile = list()
        for song in self.list:
            jsonfile.append(song.__dict__)
        with open("data/songs.json", "w") as file:
            json.dump(jsonfile, file,indent=6)

