from PIL import Image
from rich_pixels import Pixels
import pygame
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button, ListView, ListItem, Label
from textual_plotext import PlotextPlot
from hipy.parser import SongInfo, SongLibrary



class SideBar(Vertical):
    def compose(self):
        yield ListView(
            *[SideBarSongElement(song) for song in SongLibrary.songs],
            id="song-list",
        )

    def refreshList(self) -> None:
        songList = self.query_one("#song-list", ListView)
        songList.clear()
        for song in SongLibrary.songs:
            songList.append(SideBarSongElement(song))
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        songInfo = event.item.songInfo
        content = self.app.query_one("#content")
        content.remove_children()
        content.mount(SongView(songInfo))


class SideBarSongElement(ListItem):
    def __init__(self, songInfo: SongInfo, **kwargs) -> None:
        self.songInfo = songInfo
        self.songInfo.setTUISideBarElement(self)
        super().__init__(**kwargs)
    
    def compose(self):
        yield Label(self.songInfo.getGeneralInfo().get("title", "Unknown Title"))

class SongView(Vertical):
    def __init__(self, songInfo: SongInfo, **kwargs):
        self.songInfo = songInfo
        super().__init__(**kwargs)
    
    def compose(self):
        cover = self.songInfo.getImageCoverLarge()
        if cover:
            yield Static(cover, id="cover-art")
        yield Label(self.songInfo.getGeneralInfo().get("title", "Unknown Title"))
        yield Label(self.songInfo.getGeneralInfo().get("Performer", "Unknown Artist"))
        yield Label(self.songInfo.getGeneralInfo().get("album", "Unknown Album"))
        yield PlotextPlot(id="waveform")
        yield Button("▶ Play", id="play-btn")
        yield Button("⏹ Stop", id="stop-btn")

    def on_mount(self):
        plot_widget = self.query_one("#waveform", PlotextPlot)
        plt = plot_widget.plt
        plt.clear_data()
        plt.clear_figure()
        plt.theme("dark")
        waveform = self.songInfo.getWaveform()
        plt.scatter(list(range(len(waveform))), waveform)
        plt.ylim(0, 1)
        plot_widget.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "play-btn":
            pygame.mixer.music.load(self.songInfo.path)
            pygame.mixer.music.play()
        elif event.button.id == "stop-btn":
            pygame.mixer.music.stop()





        