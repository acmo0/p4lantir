from textual.widgets import RichLog
import logging
import argparse
import time

from colorlog import ColoredFormatter
from rich.logging import RichHandler
from rich.table import Table

from .config import CONFIG
from .widgets.logger import Logger


def setup_logger(logger: logging.Logger,  level=logging.INFO) -> RichLog:
    """
    Setup the logger for log file, term and app.

    :param logger: the logger to configure
    :type logger: logging.Logger
    :param level: the log level
    :type level: int
    :return: the widget where the log stream is redirected to
    :rtype: textual.widget.RichLog
    """
    logger.setLevel(level)

    # Handler for console
    term_handler = logging.StreamHandler()
    formatter = ColoredFormatter(CONFIG["LOG_FORMAT_STDOUT"])

    term_handler.setFormatter(formatter)
    logger.addHandler(term_handler)

    # Handler for file
    file_handler = logging.FileHandler(f'{CONFIG["NAME"]}-{int(time.time())}.log')
    formatter = logging.Formatter(fmt=CONFIG["LOG_FORMAT_FILE"])

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler for app
    rich_log_handler = RichHandler(
        console=Logger(id="log-displayer"),  # type: ignore
        show_time=False,
        show_path=False,
    )
    formatter = logging.Formatter(fmt=CONFIG["LOG_FORMAT_TERM"])
    rich_log_handler.setFormatter(formatter)
    logger.addHandler(rich_log_handler)

    return rich_log_handler


def setup_parser() -> argparse.ArgumentParser:
    """
    Setup the argument parser with all the script's arguments.

    :return: the argument parser
    :rtype: argparser.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog=CONFIG["NAME"],
        description="Man-in-the-Middle over TCP terminal app.")

    parser.add_argument(
        "--host-1",
        help="First host to spoof, must be the host instanciating the connection",
        required=True)

    parser.add_argument(
        "--host-2",
        help="Second host to spoof",
        required=True)

    parser.add_argument(
        "--gateway",
        help="Gateway IP",
        required=False)

    parser.add_argument(
        "-i",
        "--interface",
        help="Interface to perform arp spoofing",
        required=True)

    parser.add_argument(
        "-l",
        "--lport",
        help="Port to listen for MITM attack",
        required=True,
        type=int)

    parser.add_argument(
        "--pport",
        help="Internal port used for proxy.",
        type=int)

    parser.add_argument(
        "--debug",
        help="Enable debug mode.",
        action="store_true")

    return parser


def hexdump_view(message: bytes) -> Table:
    """
    Return a rich Table with a hexdump-like view of the messsage.

    :param message: the message to format
    :type message: bytes
    :return: rich.table.Table
    """
    # Convert printable to ascii, else set the symbol to a .
    ascii_message = "".join([chr(b) if 32 <= b < 127 else "." for b in message])

    # The constructed table from the message
    table = Table("", "hex", "printable")

    # Display length of the offset
    offset_l = len(message) // (CONFIG["DISPLAY_WIDTH"] * 256) + 1
    if offset_l % 2:
        offset_l += 1
    offset_l = max(offset_l, 4)
    offset_format = "{:0" + str(offset_l) + "x}"

    # Create the table row by row
    row_nb = len(ascii_message) // CONFIG["DISPLAY_WIDTH"] + 1
    for i in range(row_nb):
        # Compute the indexes of the start, middle and end of the flow
        # for the current line
        start_index = i * CONFIG["DISPLAY_WIDTH"]
        half_index = (2 * i + 1) * CONFIG["DISPLAY_WIDTH"] // 2
        stop_index = (i + 1) * CONFIG["DISPLAY_WIDTH"]

        # Compute the offset
        line_offset = offset_format.format(start_index)

        # Construct the hex flow
        first_hex_half = message[start_index:half_index]
        second_hex_half = message[half_index:stop_index]

        # Format the line and seperate it by more spaces in the middle
        line_hex_message = " ".join(["{:02x}".format(b) for b in first_hex_half])
        line_hex_message += "  "
        line_hex_message += " ".join(["{:02x}".format(b) for b in second_hex_half])

        # Construct the printable flow
        line_ascii_message = ascii_message[start_index:stop_index]

        # Add everything to a new row
        table.add_row(line_offset, line_hex_message, line_ascii_message)

    return table
