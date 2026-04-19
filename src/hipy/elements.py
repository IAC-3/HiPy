import sys
import json
import io
import shutil
from collections.abc import Iterable
from pathlib import Path

from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button, ListView, ListItem, Label

from hipy.parser import Song_info

class DirectoryPickerScreen(ModalScreen):
    BINDINGS = [
        ("escape", "dismiss", "Back"),
        ("enter", "confirm", "Confirm"),
        ("q", "quit", "Quit"),
    ]

    selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-container"):
            yield Static("Select a directory", id="picker-title")
            yield FilteredDirectoryTree("~/")
            with Horizontal(id="picker-buttons"):
                yield Button("Select", id="confirm-btn", variant="success")
                yield Button("Exit", id="exit-btn", variant="error")
        yield Footer()


    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.selected_path = event.path
        

    def action_confirm(self) -> None:
        if self.selected_path:
            PathHandler.add_path(self.selected_path)
            self.app.notify(f"Selected: {self.selected_path}")
            self.dismiss(self.selected_path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.action_confirm()
        elif event.button.id == "exit-btn":
            self.dismiss(None)



# removes hidden files and directories from the directory tree
class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [p for p in paths if not p.name.startswith(".")]

class Song_element(Horizontal):

    def __init__(self, song_info: Song_info, **kwargs) -> None:
        self.song_info = song_info
        super().__init__(**kwargs)

    def compose(self):
        title = self.song_info.get_general_info().get("title", "Unknown Title")
        artist = self.song_info.get_general_info().get("performer", "Unknown Artist")
        album = self.song_info.get_general_info().get("album", "Unknown Album")
        
        with Vertical(id="song-text"):
            yield Label(f"[bold]{title}[/bold]", id="song-title")
            yield Label(f"Album: {album}", id="song-album")
            yield Label(f"Artist: {artist}", id="song-artist")
        
        cover = self.song_info.get_image_cover_small()
        if cover is None:
            # Use sample.png
            from PIL import Image
            sample_path = Path("assets/sample.png")
            if sample_path.exists():
                image = Image.open(sample_path)
                image = image.resize((16, 16))
                cover = Pixels.from_image(image)
            else:
                cover = Pixels.from_image(Image.new('RGB', (16, 16), color='gray'))
        
        yield Static(cover, id="song-cover")

    def on_click(self) -> None:
        self.app.current_song = self.song_info
        preview = self.app.query_one("#preview")
        general = self.song_info.get_general_info()
        audio = self.song_info.get_audio_info()
        info = f"""[bold]Title:[/bold] {general.get("title", "Unknown")}
[bold]Artist:[/bold] {general.get("performer", "Unknown")}
[bold]Album:[/bold] {general.get("album", "Unknown")}
[bold]Format:[/bold] {general.get("format", "Unknown")}
[bold]Sample Rate:[/bold] {audio.get("sampling_rate", "Unknown")}
[bold]Bit Rate:[/bold] {audio.get("bit_rate", "Unknown")}
[bold]Bit Depth:[/bold] {audio.get("bit_depth", "Unknown")}
[bold]Channels:[/bold] {audio.get("channel_s", "Unknown")}
[bold]Lossless:[/bold] {self.song_info.is_lossless()}
[bold]Native:[/bold] {self.song_info.is_native()}
[bold]Trusted Source:[/bold] {self.song_info.is_trusted_source()}
[bold]Evaluation:[/bold] {self.song_info.get_evaluation()}

[bold]Lyrics:[/bold]
{self.song_info.get_lyrics()}
"""
        preview.update(info)


class PathHandler:
    paths: list[Path] = []

    @classmethod
    def add_path(cls, path: Path) -> None:
        cls.paths.append(path)
    
    @classmethod
    def remove_path(cls, path: Path) -> None:
        cls.paths.remove(path)
    @classmethod
    def get_paths(cls) -> list[Path]:
        return cls.paths

class RemovePathScreen(ModalScreen):
    BINDINGS = [
        ("escape", "dismiss", "Back"),
    ]

    selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-container"):
            yield Static("Select a path to remove", id="remove-title")
            yield ListView(
                *[ListItem(Label(str(p))) for p in PathHandler.paths],
                id="path-list",
            )
            with Horizontal(id="picker-buttons"):
                yield Button("Remove", id="remove-btn", variant="error")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        label = event.item.query_one(Label)
        self.selected_path = Path(label.content)
        self.app.notify(f"Selected: {self.selected_path}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "remove-btn":
            if self.selected_path:
                PathHandler.remove_path(self.selected_path)
                self.app.notify(f"Removed: {self.selected_path}")
                self.dismiss(self.selected_path)
            else:
                self.app.notify("No path selected")
        elif event.button.id == "cancel-btn":
            self.dismiss(None)