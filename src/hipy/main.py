import sys
import json
import io
from collections.abc import Iterable
from pathlib import Path
from hipy.elements import FilteredDirectoryTree, DirectoryPickerScreen, PathHandler, RemovePathScreen, Song_element

from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button

from hipy.parser import Directory_parser, Song_info, Song_library



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
            with VerticalScroll(id="sidebar"):
                pass
            with Vertical(id="content"):
                yield Static("Select a folder to get started", id="preview")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "Add_path":
            self.push_screen(DirectoryPickerScreen())
            # self.notify(self.get_screen(DirectoryPickerScreen).selected_path)
        elif event.button.id == "Remove_path":
            self.push_screen(RemovePathScreen())
        elif event.button.id == "update_songs":
            for path in PathHandler.get_paths():
                Directory_parser(path)
            sidebar = self.query_one("#sidebar")
            sidebar.remove_children()
            for song in Song_library.songs:
                name = song.get_general_info().get("title", Path(song.path).stem)
                sidebar.mount(Song_element(song, renderable=name))
            self.export_global_json()
            self.notify(f"Loaded {len(Song_library.songs)} songs and updated JSON")

    def export_global_json(self):
        songs_data = []
        for song in Song_library.songs:
            general = song.get_general_info()
            audio = song.get_audio_info()
            data = {
                "title": general.get("title", ""),
                "artist": general.get("performer", ""),
                "album": general.get("album", ""),
                "format": general.get("format", ""),
                "sample_rate": audio.get("sampling_rate", ""),
                "bit_rate": audio.get("bit_rate", ""),
                "bit_depth": audio.get("bit_depth", ""),
                "channels": audio.get("channel_s", ""),
                "lyrics": song.get_lyrics(),
                "evaluation": song.get_evaluation(),
                "lossless": song.is_lossless(),
                "native": song.is_native(),
                "trusted_source": song.is_trusted_source(),
            }
            songs_data.append(data)
        
        # Ordina per titolo
        songs_data.sort(key=lambda x: x["title"].lower())
        
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        with open(export_dir / "songs.json", "w") as f:
            json.dump(songs_data, f, indent=4)
        
        self.notify(f"Exported {len(songs_data)} songs to exports/songs.json")



    

   


def main() -> None: 
    app = HiPyApp()
    app.run()


if __name__ == "__main__":
    main()
