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

class Song_element(Static):

    def __init__(self, song_info: Song_info, renderable: str = "", **kwargs) -> None:
        self.song_info = song_info
        super().__init__(renderable, **kwargs)

    def on_click(self) -> None:
        self.app.notify(f"Selected: {self.song_info.get_general_info().get('title', Path(self.song_info.path).stem)}")


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