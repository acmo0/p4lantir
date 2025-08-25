import collections

from rich.align import Align
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, RichLog
from textual.reactive import reactive

from rich.console import Console
from ..config import CONFIG, BANNER
from ..utils import hexdump_view


class MitmAppEnter(App):
    """
    Start UI of the app
    """

    BINDINGS = [
        ("enter", "continue", "Start Attack"),
        ("escape", "close_mode", "Exit"),
    ]

    # Widget to display logs in the app
    rich_log_handler = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(auto_scroll=False)
        yield Footer(id="app-footer")
        
    def on_ready(self) -> None:
        """
        When DOM is ready, get the rich logger
        and display the banner + instructions
        """
        rich_log = self.query_one(RichLog)

        text = Align.center(
            BANNER,
            vertical="middle",
            style="bold"
        )
        instructions = Align.center(
            CONFIG["ENTER_INSTRUCTIONS"],
            style="bold italic black on white"
        )
        
        rich_log.write(text, animate=True)
        rich_log.write(instructions, animate=True)

    def on_mount(self) -> None:
        self.title = CONFIG["NAME"]
        self.sub_title = "TCP MitM Proxy"
        self.theme = CONFIG["THEME"]

    def action_close_mode(self) -> None:
        self.exit(-1)

    def action_continue(self) -> None:
        self.exit(0)