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

def get_metadata(path: str) -> str:
    mi = pymediainfo.MediaInfo.parse(path)
    return mi.to_data()

# create a parsers that visits a direcotory and finds every .mp3 / .m4a ... file inside it 
# and inside every subdirectory and creates a Song_info object for each of them and adds it to the Song_library

def Directory_parser(path: str) -> None:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith((".mp3", ".m4a", ".flac", ".wav")):
                song_path = os.path.join(root, file)
                song_info = Song_info(song_path)
                Song_library.add_song(song_info)

class Song_library:
    songs: list[Song_info] = []

    @classmethod
    def add_song(cls, song: Song_info) -> None:
        cls.songs.append(song)
    
    @classmethod
    def remove_song(cls, song: Song_info) -> None:
        cls.songs.remove(song)


class Song_info:

    def __init__(self, path: str) -> None:
        self.path = path
        self.metadata = get_metadata(path)
    

    def __str__(self) -> str:
        return f"Song_info(path={self.path}, metadata={self.metadata})"

    def get_general_info(self) -> dict:
        return self.metadata.get("tracks", [{}])[0]
    def get_audio_info(self) -> dict:
        return self.metadata.get("tracks", [{}])[1]
    
    def get_image_cover_small(self) -> Pixels:
        audio = ID3(str(self.path))
        for tag in audio.values():
            if tag.FrameID == "APIC":
                image = Image.open(io.BytesIO(tag.data))
                image = image.resize((8, 8))
                return Pixels.from_image(image)
    
    def get_image_cover_large(self) -> Pixels:
        audio = ID3(str(self.path))
        for tag in audio.values():
            if tag.FrameID == "APIC":
                image = Image.open(io.BytesIO(tag.data))
                image = image.resize((64, 64))
                return Pixels.from_image(image)