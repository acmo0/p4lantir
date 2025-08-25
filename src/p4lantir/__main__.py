import threading
import logging
import socketserver
import time
import sys
from collections import deque
from signal import SIGTERM

from .widgets.app_ui import MitmApp
from .widgets.enter_screen import MitmAppEnter
from .config import CONFIG, BANNER
from .mitm.mitm_utils import arp_spoof, setup_forwarding, get_ip_forwarding_status, stop_forwarding, get_iface_ip, get_free_port
from .mitm.proxy_server import Server
from .utils import setup_logger, setup_parser


# Setup parser and parse args
parser = setup_parser()

try:
    args = parser.parse_args()
except:
    if len(sys.argv) == 1:
        parser.print_help()
    exit(0)

# Create logger
logger = logging.getLogger()
rich_log_handler = setup_logger(
    logger=logger,
    level=logging.DEBUG if args.debug else logging.INFO
)


# Wait screen to decide wether or not to continue
entry_screen = MitmAppEnter()
user_action = entry_screen.run()

if user_action != 0:
    sys.exit(user_action)

# Intercepted message queue (thread safe)
message_queue = deque()

# Events for thread sync/actions
block_event = threading.Event()
drop_event = threading.Event()
forward_event = threading.Event()
close_event = threading.Event()
receive_event = threading.Event()

thread = None


# Set the app with it
LoggedApp = MitmApp
LoggedApp.logger = logger
LoggedApp.rich_log_handler = rich_log_handler
LoggedApp.block_event = block_event
LoggedApp.drop_event = drop_event
LoggedApp.forward_event = forward_event
LoggedApp.close_event = close_event
LoggedApp.receive_event = receive_event
LoggedApp.message_queue = message_queue

logger.debug(f"Starting programm with arguments {args}")


# Use args for listen port and proxy port
INTERFACE_IP = get_iface_ip(args.interface)
LPORT = args.lport
PROXY_PORT = get_free_port(logger, INTERFACE_IP, start=args.pport) \
             if vars(args).get("pport") \
             else get_free_port(logger, INTERFACE_IP)

# Enable ARP spoofing
setup_failed = False
spoofed_ip = args.gateway if vars(args).get("gateway") else args.host_2

try:
    process = arp_spoof(
        logger=logger,
        interface=args.interface,
        ip_addr_1=args.host_1,
        ip_addr_2=spoofed_ip)
except:
    logger.critical("Error while starting arpspoof.")
    logger.critical("please verify that the binary 'arpspoof' is present.")
    setup_failed = True

# Vaut false si l'IP forward est déjà activé
enable_ip_forward = not get_ip_forwarding_status(logger=logger)

# Active l'IP forwarding + port forwarding
if not setup_failed:
    try:
        setup_forwarding(
            logger=logger,
            interface=args.interface,
            in_port=LPORT,
            proxy_port=PROXY_PORT,
            ip_forward=enable_ip_forward)
    except Exception as e:
        logger.critical(e)
        setup_failed = True


if not setup_failed:
    try:
        ProxyServer = Server
        ProxyServer.REDIRECT_IP = args.host_2
        ProxyServer.REDIRECT_PORT = LPORT
        ProxyServer.logger = logger
        ProxyServer.block_event = block_event
        ProxyServer.drop_event = drop_event
        ProxyServer.forward_event = forward_event
        ProxyServer.close_event = close_event
        ProxyServer.message_queue = message_queue

        # Démarre le proxy
        logger.info("Starting TCP MitM Proxy")

        with socketserver.TCPServer((INTERFACE_IP, PROXY_PORT), ProxyServer) as server:
            try:
                thread = threading.Thread(target=server.serve_forever)
                thread.daemon = True
                thread.start()

                app = LoggedApp(ansi_color=True)
                app.run()

                close_event.set()
                time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                logger.warning("Catching stop signal")
            except Exception as e:
                logger.critical(e)

    except KeyboardInterrupt:
        print()
        logger.error("Interrupt")
    except Exception as e:
        logger.critical(e)

    stop_forwarding(
        logger=logger,
        interface=args.interface,
        in_port=LPORT,
        proxy_port=PROXY_PORT,
        ip_forward=enable_ip_forward)

if thread is not None:
    logger.info(
        f"Waiting for threads to stop, \
timeout is {CONFIG['WAIT_TIMEOUT']} seconds"
    )
    thread.join(timeout=CONFIG['WAIT_TIMEOUT'])

logger.info("Shutdown proxy !")

if not process.poll():
    logger.info("Killing arpspoof, please wait...")
    process.send_signal(SIGTERM)
    process.wait(timeout=30)
