import collections

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, RichLog
from textual.reactive import reactive

from ..config import CONFIG
from ..utils import hexdump_view


class PacketScreen(ModalScreen):
    """
    Showed modal to display the hexdump of a data
    """

    # Screen bindings
    BINDINGS = [
        ("escape", "app.pop_screen", "Exit")
    ]

    def __init__(self, data: bytes) -> None:
        self.data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        rich = RichLog()
        rich.write(self.data)
        yield Header()
        yield rich
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Captured data"


class MitmApp(App):
    """
    Main UI of the app
    """

    # App bindings, defined in the config.py file at the root of the module
    BINDINGS = [
        (CONFIG["CLEAR_KEY"], "clear_action", "Clear Screen"),
        (CONFIG["BLOCK_KEY"], "block_mode", "Block packets"),
        (CONFIG["DROP_KEY"], "drop_mode", "Drop packet"),
        (CONFIG["SEE_KEY"], "see_mode", "See packet"),
        (CONFIG["FORWARD_KEY"], "forward_mode", "Forward packet"),
        (CONFIG["CLOSE_KEY"], "close_mode", "Close connections"),
        (CONFIG["BLOCK_KEY"], "unblock_mode", "Unblock packets"),
    ]

    # Logger
    logger = None
    # Widget to display logs in the app
    rich_log_handler = None

    # Thread shared events to sync the UI and the TCP server
    # Tells the server to retain incoming packets
    block_event = None
    # Tells the server to drop the retained packet
    drop_event = None
    # Tells the server to forward the retained packet
    forward_event = None
    # Tells the server to close all the connections
    close_event = None

    # Shared retrained message queue (used mainly because it's thread safe)
    message_queue = reactive(collections.deque())

    # If True, then the app should display the
    # avaible bindings, including drop/forward
    block_mode = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer(id="app-footer")
        yield self.rich_log_handler.console

    def on_mount(self) -> None:
        self.title = CONFIG["NAME"]
        self.sub_title = "TCP MitM Proxy"
        self.theme = CONFIG["THEME"]

    def action_block_mode(self) -> None:
        """
        When 'b' is toggled, invert the state of the thread
        shared block event and update the available bindings
        """
        if self.block_event.is_set():
            self.block_event.clear()
            self.block_mode = False
            self.refresh_bindings()
        else:
            self.block_mode = True
            self.block_event.set()
            self.refresh_bindings()

    def action_unblock_mode(self) -> None:
        """
        Just an alias to easily change the description of the bindings
        """
        return self.action_block_mode()

    def action_drop_mode(self) -> None:
        """
        Invert the state of the thread shared drop event
        """
        if self.drop_event.is_set():
            self.drop_event.clear()
        else:
            self.drop_event.set()

    def action_forward_mode(self) -> None:
        """
        Invert the state of the thread shared forward event
        """
        if self.forward_event.is_set():
            self.forward_event.clear()
        else:
            self.forward_event.set()

    def action_close_mode(self) -> None:
        """
        Invert the state of the thread shared close connections event
        """
        if self.close_event.is_set():
            self.close_event.clear()
        else:
            self.close_event.set()

    def action_see_mode(self) -> None:
        """
        Display the intercepted packet in a hexdump-like fashion
        """
        message = self.message_queue.pop()
        self.message_queue.append(message)

        table = hexdump_view(message)

        self.push_screen(PacketScreen(data=table))
        self.refresh_bindings()

    def action_clear_action(self) -> None:
        """
        Clear the screen
        """
        self.rich_log_handler.console = self.rich_log_handler.console.clear()
        self.query_one(Header).refresh()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """
        Called automaticaly to check which binding is avaible for the user
        """

        # Change the name of the binding to activate
        # or deactivate the block mode
        if action == "block_mode":
            if self.block_mode:
                return False
            return True

        elif action == "unblock_mode":
            if self.block_mode:
                return True
            return False

        # Allow to forward/drop only when packets are blocked
        elif action in ["forward_mode", "drop_mode"]:
            if self.block_mode:
                return True
            return False

        # See only in block mode and when there is message to display
        elif action == "see_mode":
            if self.block_mode and len(self.message_queue):
                return True
            return False

        # By default, all other bindings are always available
        return True
