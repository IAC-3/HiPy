from PIL import Image
from rich_pixels import Pixels
import pygame
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Digits, DirectoryTree, Footer, Header, ProgressBar, Static, Button, ListView, ListItem, Label, SelectionList
from textual.widgets.selection_list import Selection
from textual_plotext import PlotextPlot
from hipy.parser import SongInfo, SongLibrary, PathLibrary
from hipy.player import Player


class SeekBar(ProgressBar):
    def on_click(self, event):
        if self.total and Player.isStarted():
            song = SongLibrary.get_current_song()
            if song:
                duration_ms = song.getGeneralInfo().get("duration", 0)
                if duration_ms:
                    fraction = event.x / self.size.width
                    Player.seekTo((fraction * duration_ms) / 1000)


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths):
        return [p for p in paths if not p.name.startswith(".")]


class DirectoryPickerScreen(ModalScreen):
    def compose(self):
        with Vertical(id="picker-container"):
            yield FilteredDirectoryTree("~/", id="picker-tree")
            with Horizontal(id="picker-buttons"):
                yield Button("Select", id="picker-select", variant="primary", flat=True)
                yield Button("Cancel", id="picker-cancel", flat=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "picker-select":
            tree = self.query_one("#picker-tree", DirectoryTree)
            node = tree.cursor_node
            if node and node.data and node.data.path.is_dir():
                self.dismiss(str(node.data.path))
            else:
                self.dismiss(None)
        elif event.button.id == "picker-cancel":
            self.dismiss(None)


class RemovePathScreen(ModalScreen):
    def compose(self):
        with Vertical(id="remove-path-container"):
            yield Label("Select paths to remove:")
            yield SelectionList[str](
                *[Selection(p, p) for p in PathLibrary.paths],
                id="path-selection",
            )
            with Horizontal(id="picker-buttons"):
                yield Button("Remove selected", id="remove-confirm", variant="error", flat=True)
                yield Button("Cancel", id="remove-cancel", flat=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "remove-confirm":
            selection = self.query_one("#path-selection", SelectionList)
            selected = list(selection.selected)
            self.dismiss(selected)
        elif event.button.id == "remove-cancel":
            self.dismiss(None)


class ToolBar(Horizontal):
    
    def compose(self):
        yield Button("load folder", id="load-folder-btn", variant="primary", flat=True)
        yield Button("remove paths", id="remove-path-btn", variant="error", flat=True)
        yield Button("save library", id="save-library-btn", variant="primary", flat=True)
        yield Button("clear library", id="clear-library-btn", variant="primary", flat=True)
        yield Button("⏮", id="backwards-btn",flat=True)
        yield Button("▶", id="play-btn",flat=True)
        yield Button("⏭", id="forward-btn",flat=True)
        yield SeekBar(id="progress", total=100, show_percentage=False, show_eta=False)
        
    def on_mount(self):
        self.set_interval(1 / 20, self.update_display)

    def update_display(self):
        song = SongLibrary.get_current_song()
        if song and Player.isStarted():
            duration_ms = song.getGeneralInfo().get("duration", 0)
            if duration_ms:
                pos_ms = Player.getSongPosition() * 1000
                progress = (pos_ms / duration_ms) * 100
                self.query_one("#progress", SeekBar).update(progress=min(progress, 100))
        else:
            self.query_one("#progress", SeekBar).update(progress=0)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load-folder-btn":
            self.app.push_screen(DirectoryPickerScreen(), self.app.on_folder_selected)
        elif event.button.id == "remove-path-btn":
            self.app.push_screen(RemovePathScreen(), self.app.on_paths_removed)
        elif event.button.id == "save-library-btn":
            SongLibrary.saveLibrary("library.json")
        elif event.button.id == "clear-library-btn":
            SongLibrary.clearLibrary()
            sidebar = self.app.query_one(SideBar)
            sidebar.refreshList()
        elif event.button.id == "backwards-btn":
            prev_song = SongLibrary.getPreviousSong()
            if prev_song:
                Player.playSong(prev_song)
        elif event.button.id == "play-btn":
            if not Player.isStarted():
                Player.playSong(SongLibrary.get_current_song())
            else:
                event.button.label = "⏸" if not Player.isPlaying() else "▶"
                Player.togglePause()
        elif event.button.id == "forward-btn":
            next_song = SongLibrary.getNextSong()
            if next_song:
                Player.playSong(next_song)


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
        SongLibrary.set_current_song(songInfo)
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
        self.log(f"Creating SongView for {self.songInfo.path}")
        super().__init__(**kwargs)
    
    def compose(self):
        cover = self.songInfo.getImageCoverLarge()
        if cover:
            yield Static(cover, id="cover-art")
        yield Label(self.songInfo.getGeneralInfo().get("title", "Unknown Title"), id="title")
        yield Label(self.songInfo.getGeneralInfo().get("performer", "Unknown Artist"), id="performer")
        yield Label(self.songInfo.getGeneralInfo().get("album", "Unknown Album"), id="album")
        yield Label(f"Bitrate: {self.songInfo.getBitRate()} {self.songInfo.getBitRateMode()}", id="bitrate")
        yield Label(f"Sample Rate: {self.songInfo.getSampleRate()} Hz", id="samplerate")   
        yield Label(f"Duration: {(self.songInfo.getGeneralInfo().get('duration', 0))/60000} minutes", id="duration")   

        
        

  

   





        