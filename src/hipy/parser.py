from email.mime import audio
import io
import json
import os
from pygments.token import String
import pymediainfo
from pathlib import Path
from PIL import Image
from rich_pixels import Pixels
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import librosa
import numpy as np
from tinydb import TinyDB

DEFAULT_COVER = Path(__file__).parent.parent.parent / "assets" / "sample.png"



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

    def getBitRateMode(self) -> int:
        return self.getGeneralInfo().get("overall_bit_rate_mode", "Unknown")

    def getBitRate(self) -> int:
        return self.getGeneralInfo().get("overall_bit_rate", "Unknown")

    def getSampleRate(self) -> int:
        return int(self.getAudioInfo().get("sampling_rate", 44100))

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
        return Pixels.from_image(Image.open(DEFAULT_COVER).resize((8, 8)))
    
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
        return Pixels.from_image(Image.open(DEFAULT_COVER).resize((48, 48)))
    
    def getLyrics(self) -> str:
        try:
            audio = ID3(str(self.path))
            for tag in audio.values():
                if tag.FrameID == "USLT":
                    return tag.text
        except:
            pass
        return ""
    
    def getWaveform(self, num_points=200):
        y, sr = librosa.load(self.path, sr=None, mono=True)
        if len(y) == 0:
            return [0.0] * num_points
        num_points = min(num_points, len(y))
        chunk_size = len(y) // num_points
        waveform = np.array([
            np.max(np.abs(y[i * chunk_size:(i + 1) * chunk_size]))
            for i in range(num_points)
        ])
        waveform = waveform / (np.max(waveform) + 1e-10)
        return waveform.tolist()
    
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
    currentSong: SongInfo = None

    @classmethod
    def addSong(cls, song: SongInfo) -> None:
        cls.songs.append(song)
    
    @classmethod
    def set_current_song(cls, song: SongInfo) -> None:
        cls.currentSong = song  
    
    @classmethod
    def get_current_song(cls) -> SongInfo:
        return cls.currentSong  

    @classmethod
    def getNextSong(cls) -> SongInfo:
        if not cls.songs or cls.currentSong is None:
            return None
        idx = cls.songs.index(cls.currentSong)
        if idx + 1 < len(cls.songs):
            cls.currentSong = cls.songs[idx + 1]
            return cls.currentSong
        return None

    @classmethod
    def getPreviousSong(cls) -> SongInfo:
        if not cls.songs or cls.currentSong is None:
            return None
        idx = cls.songs.index(cls.currentSong)
        if idx - 1 >= 0:
            cls.currentSong = cls.songs[idx - 1]
            return cls.currentSong
        return None

    @classmethod
    def saveLibrary(cls, path: str) -> None:
        db_path = Path(path)
        if db_path.exists():
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if not isinstance(existing, dict):
                    with open(db_path, "w", encoding="utf-8") as f:
                        json.dump({}, f)
            except Exception:
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)

        db = TinyDB(path)
        songs_table = db.table("songs")
        songs_table.truncate()
        songs_table.insert_multiple(
            [{"path": song.path, "metadata": song.metadata} for song in cls.songs]
        )
        db.close()

    @classmethod
    def addSongsFromDirectory(cls, directory: str) -> bool:
        added = False
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in musicExtensions):
                    song_path = os.path.join(root, file)
                    cls.addSong(SongInfo(song_path))
                    added = True
        return added

    @classmethod
    def removeSong(cls, song: SongInfo) -> None:
        cls.songs.remove(song)

class PathLibrary:
    paths: list[str] = []

    @classmethod
    def addPath(cls, path: str) -> None:
        cls.paths.append(path)
    
    @classmethod
    def removePath(cls, path: str) -> None:
        cls.paths.remove(path)