import serial
import logging

import subprocess
logger = logging.getLogger(__name__)
import socket
import nmap
import pytz, tzlocal
from configparser import ConfigParser
from odm360.states import states


def cleanopts(optsin):
    """Takes a multidict from a flask form, returns cleaned dict of options"""
    opts = {}
    d = optsin
    for key in d:
        opts[key] = optsin[key].lower().replace(" ", "_")
    return opts


def find_serial(wildcard="", logger=logger):
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
            logger.info(f"Found {description} on port {port}")
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
    s.connect(("<broadcast>", 0))
    return s.getsockname()[0]


def get_lan_devices(ip_subnet):
    """

    :return:
    """
    ip_parts = ip_subnet.split(".")
    if len(ip_parts) < 3:
        raise ValueError(
            'You supplied an ip_subnet that does not look like "XXX.XXX.XXX.XXX"'
        )
    ip_subnet = "{}.{}.{}.0/24".format(*ip_parts[0:3])

    nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
    nm.scan(hosts=ip_subnet, arguments="-sP")
    return [(x, nm[x]["status"]["state"]) for x in nm.all_hosts()]


def to_utc(dt):
    """
    convert timezone to utc timezone, assuming it is in local time.
    :param dt: datetime obj
    :return: datetime obj
    """

    dt_local = dt.astimezone()
    return dt_local.astimezone(pytz.utc)


def to_local_tz(dt):
    """
    convert timezone aware datetime object to local timezone. If no timezone is provided it will return the same
    dt, assuming it is local timezone
    :param dt: datetime obj
    :return: datetime obj
    """
    local_tz = tzlocal.get_localzone()
    return dt.astimezone(local_tz)


def get_key_state(value):
    """
    Returns the key in dict "states" belonging to provided value. If the key is ambiguous, a list of keys is provided.
    If value is not found in dict, None is returnewd
    :param value: int - state value to look for key
    :return: str - name of key
    """
    keys = [k for k, v in states.items() if v == value]
    if len(keys) == 0:
        return None
    elif len(keys) == 1:
        return keys[0]
    else:
        return keys


def create_geo_txt(
    fns,
    proj="EPSG:4326",
    fn_key="photo_filename",
    x_key="lon",
    y_key="lat",
    z_key="alt",
    acc_x_key="epx",
    acc_y_key="epy",
    acc_z_key="epv",
):

    """
    prepare a string containing a geo.txt file, ready for use on ODM

    """

    template = "{:s} {:.8f} {:.8f} {:.8f} 0 0 0 {:.5f} {:.4f}\n".format
    geo = ""
    geo += f"{proj}\n"
    for fn in fns:
        # check if all keys are present (i.e. not None)
        if all(
            [
                fn[k] is not None
                for k in [fn_key, x_key, y_key, z_key, acc_x_key, acc_y_key, acc_z_key]
            ]
        ):
            # parse line, take average of x and y error
            geo += template(
                fn[fn_key],
                fn[x_key],
                fn[y_key],
                fn[z_key],
                (fn[acc_x_key] + fn[acc_y_key]) * 0.5,
                fn[acc_z_key],
            )
    return geo

def add_wifi(ssid, passkey, wpa_file="/etc/wpa_supplicant/wpa_supplicant.conf"):
    """
    Add a WiFi network name and PSK to /etc/wpa_supplicant/wpa_supplicant.conf
    Taken from https://www.raspberrypi.org/forums/viewtopic.php?t=216506
    """
    template = """
network={{
    ssid="{:s}"
    psk="{:s}"
}}""".format

    p1 = subprocess.Popen(["echo", template(ssid, passkey)], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sudo", "tee", "-a", "/etc/wpa_supplicant/wpa_supplicant.conf", ">", "/dev/null"],
                          stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Give p1 a SIGPIPE if p2 dies.
    output, err = p2.communicate()
    return output, err
