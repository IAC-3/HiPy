import sys
import json
import io
import pygame
from collections.abc import Iterable
from pathlib import Path
from hipy.TUI.elements import SideBarSongElement, SideBar

from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button, ListView, ListItem, Label

from hipy.parser import SongInfo, SongLibrary



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
        self.currentSong = None

    def compose(self) -> ComposeResult:
        # yield Header()
        with Horizontal(id="main-area"):
            with VerticalScroll(id="sidebar"):
                yield SideBar()
            with Vertical(id="content"):
                yield Static("Select a folder to get started", id="preview")  
        yield Footer()

    



    

   


def main() -> None: 
    SongLibrary.addSongsFromDirectory("/Users/marcomattiuz/Music/Music/Media.localized/Music")
 


    app = HiPyApp()
    app.run()


if __name__ == "__main__":
    main()
