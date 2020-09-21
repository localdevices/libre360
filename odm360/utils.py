import serial
import logging

logger = logging.getLogger(__name__)
import socket
import nmap
from configparser import ConfigParser


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

def parse_config(settings_path):
    """
        Parse the config file with interpolation=None or it will break run_cast.sh
    """
    config = ConfigParser(interpolation=None)
    config.read(settings_path)
    return config

def make_config(settings):
    """
    Writes a config to a file

    :param settings_path:
    :return:
    """
    config = ConfigParser()
    config.add_section('main')
    for setting in settings:
        config.set('main', setting, settings[setting])
    return config

def to_utc(dt):
    dt_local = dt.astimezone()
    return dt_local.astimezone(pytz.utc)
import pytz, datetime
local = pytz.timezone ("America/Los_Angeles")
naive = datetime.datetime.strptime ("2001-2-3 10:11:12", "%Y-%m-%d %H:%M:%S")
local_dt = local.localize(naive, is_dst=None)
utc_dt = local_dt.astimezone(pytz.utc)