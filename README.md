<div align="center">

# p4lantir

![](https://raw.githubusercontent.com/acmo0/p4lantir/main/imgs/logo.svg)


![PyPI - Version](https://img.shields.io/pypi/v/p4lantir?style=plastic)
![PyPI - License](https://img.shields.io/pypi/l/p4lantir)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Facmo0%2Fp4lantir%2Fmain%2Fpyproject.toml)

</div>

***

**p4lantir** is a simple tool to perform Man-in-the-Middle over TCP using ARP spoofing, allowing to intercept, drop, forward and see TCP flows.

This project is intended to be relatively simple, making simple future contributions for new features/bug fix.

> [!CAUTION]
> This ethical hacking project is intended for educational purposes and awareness training sessions only. I decline all responsability about the usage of this project.

***

## Screenshots

![p4lantir-screen1](https://raw.githubusercontent.com/acmo0/p4lantir/main/imgs/screenshot-1.png)
![p4lantir-screen2](https://raw.githubusercontent.com/acmo0/p4lantir/main/imgs/screenshot-2.png)
![p4lantir-screen3](https://raw.githubusercontent.com/acmo0/p4lantir/main/imgs/screenshot-3.png)
![p4lantir-screen4](https://raw.githubusercontent.com/acmo0/p4lantir/main/imgs/screenshot-4.png)


## Installation
- Install the system dependencies (arpspoof, iptables)
- Create python virtual environnement
- Install the package

Setup instructions :
- [Debian-based (Debian, Kali, Ubuntu,...)](#debian-based-systems)
- [Archlinux](#archlinux)

### Debian-based systems
```bash
sudo apt install dsniff iptables

python3 -m venv venv
source venv/bin/activate

pip install p4lantir
```

### Archlinux
```bash
pacman -S dsniff iptables

python3 -m venv venv
source venv/bin/activate

pip install p4lantir
```

> Note : the package can also be downloaded from the release and installed using the `.whl` file and `pip`.

## Usage
> [!WARNING]
> You need to run the script as root due to arpspoof and iptables. You should open a shell as root, activate the venv and then use *p4lantir*.
```
usage: p4lantir [-h] --host-1 HOST_1 --host-2 HOST_2 [--gateway GATEWAY] -i INTERFACE -l LPORT [--pport PPORT] [--debug]

Man-in-the-Middle over TCP terminal app.

options:
  -h, --help            show this help message and exit
  --host-1 HOST_1       First host to spoof, must be the host instanciating the connection
  --host-2 HOST_2       Second host to spoof
  --gateway GATEWAY     Gateway IP
  -i, --interface INTERFACE
                        Interface to perform arp spoofing
  -l, --lport LPORT     Port to listen for MITM attack
  --pport PPORT         Internal port used for proxy.
  --debug               Enable debug mode.
```

### Examples
#### Client/server in the same localhost

Let say that a client at IP *C* connect to a remote server at IP *R*, both in the same LAN. You need to know the name of the interface that connects you this LAN (let call this *iface*. Then your command should look like :
```bash
p4lantir --host-1 [replace with C] \
         --host-2 [replace with R] \
         -i [replace with iface] \
         -lport [server's listening port]
```

> About the listening port, if you intend to intercept SMTP you may choose `25`, `80` for HTTP, and so on ...

### Client/server on a different LAN

If the client is in the same LAN as you and the server is not in your LAN, then you have to add another parameter : the gateway IP. *p4lantir* will then spoof the gateway IP and open a connection to the server.
```bash
p4lantir --host-1 [replace with C] \
         --host-2 [replace with R] \
         --gateway [replace with gw's IP]
         -i [replace with iface] \
         -lport [server's listening port]
```

## Documentation
The source-code documentation is available [here](https://www.acmo0.org/p4lantir/)


## Contributing
**All contributions are welcome !**

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for more details.

## License
This project is under the GPL-v3 license, please see [LICENSE.TXT](./LICENSE.TXT)
