import sys
import json
import io
import pygame
from collections.abc import Iterable
from pathlib import Path
from hipy.TUI.elements import SideBarSongElement, SideBar, ToolBar, DirectoryPickerScreen, RemovePathScreen

from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button, ListView, ListItem, Label

from hipy.parser import SongInfo, SongLibrary,PathLibrary



class HiPyApp(App):
    """A cool music companion."""

    TITLE = "HiPy"
    CSS_PATH = "main.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        pygame.mixer.init()

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-area"):
                yield ToolBar()
        with Horizontal(id="main-area"):
            with VerticalScroll(id="sidebar"):
                yield SideBar()
            with Vertical(id="content"):
                yield Static("Select a folder to get started", id="preview")  
        yield Footer()

    def on_folder_selected(self, path: str | None) -> None:
        if path is None or SongLibrary.addSongsFromDirectory(path) is False or path in PathLibrary.paths:
            return
        PathLibrary.addPath(path)

        if SongLibrary.addSongsFromDirectory(path):
            sidebar = self.query_one(SideBar)
            sidebar.refreshList()
        else:
            self.notify(f"No music files found in {path}", severity="error")

    def on_paths_removed(self, paths: list[str] | None) -> None:
        if not paths:
            return
        for p in paths:
            PathLibrary.removePath(p)
            SongLibrary.songs = [
                s for s in SongLibrary.songs
                if not s.path.startswith(p)
            ]
        sidebar = self.query_one(SideBar)
        sidebar.refreshList()

    



    

   


def main() -> None: 
   
 


    app = HiPyApp()
    app.run()


if __name__ == "__main__":
    main()
