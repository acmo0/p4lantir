import logging
from textual.widgets import RichLog
from textual.widget import Widget


class SpecialHandler(logging.Handler):

    def __init__(self, sender) -> None:
        self.sender = sender
        logging.Handler.__init__(self=self)

    def emit(self, record) -> None:
        self.sender.emptiness = str(record)


class Logger(RichLog):
    file = False
    console: Widget

    def print(self, content) -> None:
        try:
            self.write(content)
        except:
            pass
