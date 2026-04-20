
import pygame

from hipy.parser import SongLibrary


class Player:
    current_song = None
    _started = False
    _paused = False

    @classmethod
    def playSong(cls, song):
        cls.current_song = SongLibrary.get_current_song()
        if cls.current_song:
            sr = cls.current_song.getSampleRate()
            pygame.mixer.quit()
            pygame.mixer.init(frequency=sr, size=-16, channels=2, buffer=2048)
            pygame.mixer.music.load(cls.current_song.path)
            pygame.mixer.music.play()
            cls._started = True
            cls._paused = False
    
    @classmethod
    def stopSong(cls):
        pygame.mixer.music.stop()
        cls.current_song = None
        cls._started = False
        cls._paused = False
        SongLibrary.set_current_song(None)

    @classmethod
    def togglePause(cls):
        if cls._paused:
            pygame.mixer.music.unpause()
            cls._paused = False
        else:
            pygame.mixer.music.pause()
            cls._paused = True

    @classmethod
    def isStarted(cls) -> bool:
        return cls._started

    @classmethod
    def isPlaying(cls) -> bool:
        return cls._started and not cls._paused

    @classmethod
    def getSongPosition(cls) -> float:
        if cls._started:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0

    @classmethod
    def seekTo(cls, seconds: float):
        if cls._started and cls.current_song:
            pygame.mixer.music.play(start=seconds)


        