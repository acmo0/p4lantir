import logging
import subprocess
import socket
import struct
import fcntl


def arp_spoof(logger: logging.Logger,
              interface: str,
              ip_addr_1: str,
              ip_addr_2: str) -> subprocess.Popen:
    """
    Enable ARP Spoofing between IPs `ip_addr_1` and `ip_addr_2` on the interface `interface`

    :param interface: The interface to start the ARP spoofing
    :type interface: str
    :param ip_addr_1: The IP to send the ARP spoofing packets
    :type ip_addr_1: str
    :param ip_addr_2: The IP to spoof
    :type ip_addr_2: str
    :return: The `arpspoof` process
    :rtype: subprocess.Popen
    """

    logger.info(f"Starting ARP spoofing between {ip_addr_1} and {ip_addr_2}")
    return subprocess.Popen(
        ["arpspoof", "-i", interface, "-t", ip_addr_1, ip_addr_2, "-r"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def setup_forwarding(logger: logging.Logger,
                     interface: str,
                     in_port: int,
                     proxy_port: int,
                     ip_forward: bool) -> None:
    """
    Enable IP forwarding and port redirection
    to forward incoming packets to the internal TCP sever

    :param interface: The interface on which the port redirection will be enabled
    :type interface: str
    :param in_port: The port from which the TCP flow should arrive
    :type in_port: int
    :param proxy_port: The internal TCP server port
    :type proxy_port: int
    :param ip_forward: Enable or not the IP forwarding
    :type ip_forward: bool
    """
    if ip_forward:
        logger.info("Enable IPv4 forwarding")
        subprocess.call(
            ["sysctl", "-w", "net.ipv4.ip_forward=1"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

    logger.info(f"Setup port redirection to proxy {in_port} -> {proxy_port}")
    c = subprocess.Popen(
        [
            "iptables",
            "-t", "nat",
            "-A", "PREROUTING",
            "-i", interface,
            "-p", "tcp",
            "--dport", str(in_port),
            "-j", "REDIRECT",
            "--to-port", str(proxy_port)
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL)
    c.wait(timeout=15)

    if c.returncode:
        with c.stderr:
            logger.critical(
                f"From iptables \"{c.stderr.read().decode().strip()}\""
            )
            raise subprocess.CalledProcessError(c.returncode, c.args)


def get_ip_forwarding_status(logger: logging.Logger) -> bool:
    """
    Detect if the IP forwarding is already activated on the computer

    :return: True if IP forwarding is enabled, False otherwise
    :rtype: bool
    """
    with open("/proc/sys/net/ipv4/ip_forward", "r") as f:
        try:
            return int(f.read().strip()) == 1
        except:
            logger.error(
                "Unable to check IP forwarding status, consider as deactivated"
                )
            return False


def stop_forwarding(logger: logging.Logger,
                    interface: str,
                    in_port: int,
                    proxy_port: int,
                    ip_forward: bool) -> None:
    """
    Deactivate IP forwarding if `ip_forward` is True and stop port redirection.

    :param interface: The interface on wich disable the port redirection
    :type interface: str
    :param in_port: The port on which the incoming TCP flow arrive
    :type in_port: int
    :param proxy_port: The internal TCP server port
    :type proxy_port: int
    :param ip_forward: Disable or not IP forwarding
    :type ip_forward: bool
    """
    # Disable the IP forwarding
    if ip_forward:
        logger.info("Disable IPv4 forwarding")
        subprocess.call(
            ["sysctl", "-w", "net.ipv4.ip_forward=0"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

    logger.info(f"Stop port redirection to proxy {in_port} -> {proxy_port}")

    # Disable the port forwarding
    c = subprocess.Popen(
        [
            "iptables",
            "-t", "nat",
            "-D", "PREROUTING",
            "-i", interface,
            "-p", "tcp",
            "--dport", str(in_port),
            "-j", "REDIRECT",
            "--to-port", str(proxy_port)
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL
    )
    c.wait(timeout=15)

    if c.returncode:
        with c.stderr:
            logger.critical(
                f"From iptables \"{c.stderr.read().decode().strip()}\""
            )


def get_iface_ip(interface: str) -> str:
    """
    Retrieve the interface's IP from its name.

    :param interface: the interface name
    :type interface: str
    :returns: the interface's IP
    :rtype: str
    """

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        packed_iface = struct.pack(
            '256s',
            interface.encode('utf_8')
        )
        packed_addr = fcntl.ioctl(
            s.fileno(),
            0x8915,
            packed_iface
        )[20:24]

        return socket.inet_ntoa(packed_addr)


def get_free_port(logger: logging.Logger, interface_ip: str, start: int = 1025) -> None | int:
    """
    Get the first bindable port starting from `start`.

    :param logger: the logger to display debug information
    :type logger: logging.Logger
    :param interface_ip: the IP to bind the port
    :type interface_ip: str
    :param start: the first port to test if bindable
    :type start: int
    :return: a bindable port > start
    :rtype: int
    """
    for port in range(start, 65534):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((interface_ip, port))
        except socket.error as e:
            logger.debug(f"Unable to bind {interface_ip}:{port}, from socket : {e}")
        else:
            return port
