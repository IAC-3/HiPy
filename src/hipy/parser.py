from email.mime import audio
import io
import json
import os
import pymediainfo
from pathlib import Path
from PIL import Image
from rich_pixels import Pixels
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

musicExtensions = [".mp3", ".flac", ".wav", ".alac", ".dsd", ".aac", ".ogg", ".opus"]

def getMetadata(path: str) -> str:
    mi = pymediainfo.MediaInfo.parse(path)
    return mi.to_data()




class SongInfo:

    def __init__(self, path: str) -> None:
        self.path = path
        self.metadata = getMetadata(path)
    

    def __str__(self) -> str:
        return f"SongInfo(path={self.path}, metadata={self.metadata})"

    def setTUISideBarElement(self, element) -> None:
        self.tuiSideBarElement = element
    
    def getTUISideBarElement(self):
        return getattr(self, "tuiSideBarElement", None)
    
    def setTUIContentElement(self, element) -> None:
        self.tuiContentElement = element
    
    def getTUIContentElement(self):
        return getattr(self, "tuiContentElement", None)

    def getGeneralInfo(self) -> dict:
        return self.metadata.get("tracks", [{}])[0]
    
    def getAudioInfo(self) -> dict:
        return self.metadata.get("tracks", [{}])[1]
    
    def getImageCoverSmall(self) -> Pixels:
        try:
            audio = ID3(str(self.path))
            for tag in audio.values():
                if tag.FrameID == "APIC":
                    image = Image.open(io.BytesIO(tag.data))
                    image = image.resize((8, 8))
                    return Pixels.from_image(image)
        except:
            pass
        return None
    
    def getImageCoverLarge(self) -> Pixels:
        try:
            audio = ID3(str(self.path))
            for tag in audio.values():
                if tag.FrameID == "APIC":
                    image = Image.open(io.BytesIO(tag.data))
                    image = image.resize((48, 48))
                    return Pixels.from_image(image)
        except:
            pass
        return None
    
    def getLyrics(self) -> str:
        try:
            audio = ID3(str(self.path))
            for tag in audio.values():
                if tag.FrameID == "USLT":
                    return tag.text
        except:
            pass
        return ""
    
    def isLossless(self) -> bool:
        format = self.getGeneralInfo().get("format", "").lower()
        return format in ["flac", "wav", "alac", "dsd"]
    
    def isNative(self) -> bool:
        # Da definire: forse se è in formato originale senza conversione
        # Per ora, assumiamo True se lossless
        return self.isLossless()
    
    def isTrustedSource(self) -> bool:
        # Flag manuale, per ora False
        return False
    
    def getEvaluation(self) -> float:
        # Campo da implementare, per ora 0.0
        return 0.0


class SongLibrary:
    songs: list[SongInfo] = []

    @classmethod
    def addSong(cls, song: SongInfo) -> None:
        cls.songs.append(song)
    
    @classmethod
    def addSongsFromDirectory(cls, directory: str) -> None:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in musicExtensions):
                    song_path = os.path.join(root, file)
                    cls.addSong(SongInfo(song_path))

    @classmethod
    def removeSong(cls, song: SongInfo) -> None:
        cls.songs.remove(song)

    @classmethod
    def saveLibrary(cls, path: str) -> None:
        with open(path, "w") as f:
            json.dump([song.__dict__ for song in cls.songs], f, indent=2)

