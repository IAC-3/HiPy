import sys
import json
import io
from collections.abc import Iterable
from pathlib import Path
from hipy.elements import FilteredDirectoryTree, DirectoryPickerScreen

from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button

from hipy.parser import Song_info



class HiPyApp(App):
    """A cool music companion."""

    TITLE = "HiPy"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="toolbar"):
            yield Button("Add path", id="Add_path", variant="success")
            yield Button("Remove path", id="Remove_path", variant="error")
            yield Button("Update songs", id="update_songs", variant="primary")
        with Horizontal(id="main-area"):
            with Vertical(id="sidebar"):
                yield Static("Sidebar", id="sidebar-content")
            with Vertical(id="content"):
                yield Static("Select a folder to get started", id="preview")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "Add_path":
            self.push_screen(DirectoryPickerScreen())
            # self.notify(self.get_screen(DirectoryPickerScreen).selected_path)
        elif event.button.id == "Remove_path":
            self.notify("Remove path clicked")
        elif event.button.id == "update_songs":
            self.notify("Update songs clicked")



    

   


def main() -> None: 
    app = HiPyApp()
    app.run()


if __name__ == "__main__":
    main()
