from email.mime import audio
import io
import json
import pymediainfo
from pathlib import Path
from PIL import Image
from rich_pixels import Pixels
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

def get_metadata(path: str) -> str:
    mi = pymediainfo.MediaInfo.parse(path)
    return mi.to_data()




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