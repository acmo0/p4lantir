import socketserver
import socket
import logging
import selectors
import time

from ..config import CONFIG


class Server(socketserver.BaseRequestHandler):
    """
    TCP Proxy/relay server for Man-in-the-Middle attacks.
    """

    BUFF_SIZE = 4096
    REDIRECT_IP = None
    REDIRECT_PORT = None

    logger = None
    block_event = None
    drop_event = None
    forward_event = None
    receive_event = None

    message_queue = None

    BLOCK_MESSAGE = f"Packet blocked ('{CONFIG['SEE_KEY']}' to see it)"

    def handle(self) -> None:
        """
        Called method at each initiated connexion.
        """
        # Init logger
        if not self.logger:
            self.logger = logging.getLogger("server")

        self.logger.info(
            f"Opening connection for client {self.client_address[0]}"
        )

        if self.close_event.is_set():
            self.close_socket("client")
            return

        # Connect to the spoofed server
        self.open_connexion_to_server()

        # Register socket selector to handle
        # incoming packets in both directions
        self.sel = selectors.DefaultSelector()
        self.sel.register(
            self.request,
            selectors.EVENT_READ,
            data={"from": "client", "to": "server"},
        )
        self.sel.register(
            self.socket,
            selectors.EVENT_READ,
            data={"from": "server", "to": "client"},
        )

        # Sockets must be set as non blocking
        # for it to work
        self.request.setblocking(0)
        self.socket.setblocking(0)

        while not self.close_event.is_set():
            # Retrieve socket events
            events = self.sel.select()

            for key, mask in events:
                # setup client socket connection
                if key.data is None:
                    self.logger.error("Got none data")

                # If incomming packets
                elif mask & selectors.EVENT_READ:
                    self.logger.debug("Read event !")
                    
                    # Receive data from client or server
                    data = self.recv_from(key.data["from"])

                    self.message_queue.clear()
                    self.message_queue.append(data)
                    
                    # If nothing, then close the sockets
                    if not data:
                        self.close_sockets()
                        return

                    # Else, handle the incoming packets
                    else:
                        # If block packets, display help message
                        if self.block_event.is_set():
                            self.logger.warning(
                                self.BLOCK_MESSAGE
                            )

                        # Wait until a user action/unblock
                        while self.block_event.is_set():
                            time.sleep(0.1)

                            # Close sockets
                            if self.close_event.is_set():
                                self.close_sockets()
                                return

                            # Exit if an action is taken by user
                            if self.drop_event.is_set() or self.forward_event.is_set():
                                break

                        # If the user wants to drop
                        if self.drop_event.is_set():
                            self.drop_event.clear()

                            # Log with a <DROPPED> prefix
                            self.log_transfer(
                                src=key.data["from"],
                                dst=key.data["to"],
                                data=data,
                                note=CONFIG["DROPPED_NOTE"])

                        # Otherwise, forward it
                        else:
                            self.logger.debug(
                                f"Sending message to {key.data['to']}"
                            )

                            # Forward to right direction
                            if key.data["from"] == "client":
                                self.socket.send(data)
                            else:
                                self.request.send(data)

                            self.logger.debug(
                                f"Sended message to {key.data['to']}"
                            )

                            # Print the forwarded message
                            self.log_transfer(
                                src=key.data["from"],
                                dst=key.data["to"],
                                data=data,
                                note=CONFIG["FORWARDED_NOTE"] \
                                     if self.forward_event.is_set() else "")

                            self.forward_event.clear()

            time.sleep(0.001)

        self.logger.warning("End of interception")
        # Ferme la connection avec le serveur
        self.close_sockets()

    def open_connexion_to_server(self) -> None:
        """
        Open a TCP connection with the spoofed server to forward/receive packets.
        """
        self.logger.info(
            f"Opening connection to server at {self.REDIRECT_IP}:{self.REDIRECT_PORT}"
        )

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.REDIRECT_IP, self.REDIRECT_PORT))

    def recv_from(self, src: str) -> bytes:
        """
        Receive a message over TCP from the client or the server

        :param src: Source of the incoming packets
        :type src: str
        :return: Received data
        :rtype: bytes
        """
        recv = None

        if src == "client":
            recv = self.request.recv(self.BUFF_SIZE)
        elif src == "server":
            recv = self.socket.recv(self.BUFF_SIZE)
        else:
            raise ValueError("Unknow dest, must be 'client' or 'server'")

        if not recv:
            self.logger.warning(f"Nothing received from {src}")
        else:
            self.logger.debug(f"Received from {src} : {recv}")

        return recv

    def close_socket(self, socket_name: str) -> None:
        """
        Close a socket, either the server's one or the client's one.

        :param socket_name: le name of the socket to close (client/server)
        :type socket_name: str
        """

        if socket_name == "client":
            self.logger.warning("Closing client's socket")
            self.request.shutdown(socket.SHUT_RDWR)
        elif socket_name == "server":
            self.logger.warning("Closing server's socket")
            self.socket.shutdown(socket.SHUT_RDWR)
        else:
            raise ValueError("Unknow dest, must be 'client' or 'server'")

    def close_sockets(self) -> None:
        """
        Close both client's and server's opened socket
        """
        self.logger.warning("Closing connections")
        self.close_socket("server")
        self.close_socket("client")

    def log_transfer(self, src: str, dst: str, data: bytes, note: str = "") -> None:
        """
        Log the received and then forwarded/dropper packets in a fancy way.
        """
        if note == "":
            try:
                self.logger.info(f"({src} -> {dst}) : {data.decode()}")
            except:
                self.logger.info(f"({src} -> {dst}) : {data.hex()}\t{data}")
        else:
            try:
                self.logger.warning(f"{note}({src} -> {dst}) : {data.decode()}")
            except:
                self.logger.warning(f"{note}({src} -> {dst}) : {data.hex()}\t{data}")
