import serial
import logging
logger = logging.getLogger(__name__)
import socket
import nmap


def find_serial(wildcard='', logger=logger):
    """
    Looks for serial devices in all active serial ports

    :param wildcard: str - wildcard used to look for serial device (default: empty)
    """
    ps = list(serial.tools.list_ports.comports())
    ports = []
    descr = []
    for p in ps:
        port = p[0]
        description = p[1]
        if wildcard.lower() in description.lower():
            logger.info(f'Found {description} on port {port}')
            ports.append(port)
            descr.append(description)
    return ports, descr

def get_lan_ip():
    """
    Retrieves LAN network IP address with just the socket lib

    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

def get_lan_devices(ip_subnet):
    """

    :return:
    """
    ip_parts = ip_subnet.split('.')
    if len(ip_parts) < 3:
        raise ValueError('You supplied an ip_subnet that does not look like "XXX.XXX.XXX.XXX"')
    ip_subnet = '{}.{}.{}.0/24'.format(*ip_parts[0:3])

    nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
    nm.scan(hosts=ip_subnet, arguments='-sP')
    return [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
