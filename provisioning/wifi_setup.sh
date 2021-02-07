#!/bin/bash

# Set up WiFi on parent raspberry pi (called from parent_pi_setup.sh)
# recipe from https://learn.sparkfun.com/tutorials/setting-up-a-raspberry-pi-3-as-an-access-point/all

echo "Installing hostapd and dnsmasq"
sudo apt install -y hostapd dnsmasq
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
echo "enabling hostapd service"
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

echo "Setting up local access point via wlan0"
# add denyinterfaces to dhcp conf
sudo echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf

echo $'auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.5.1
    netmask 255.255.255.0
    network 192.168.5.0
    broadcast 192.168.5.255
' | sudo tee -a /etc/network/interfaces

echo $'interface=wlan0
driver=nl80211
ssid=odm360
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=zanzibar
rsn_pairwise=CCMP
' | sudo tee /etc/hostapd/hostapd.conf

sudo sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/g' /etc/default/hostapd

# prepare fixed IP address and DHCP address range
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
echo $'interface=wlan0
listen-address=192.168.5.1
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=192.168.5.100,192.168.5.200,24h
' | sudo tee /etc/dnsmasq.conf

echo "Establishing bridge for internet connection"
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1"/g' /etc/sysctl.conf
echo $'
net.ipv4.ip_forward=1
' | sudo tee /etc/sysctl.d/routed-ap.conf

# check if there is a wlan usb device. If not go for eth0 routing
if (ip addr) | grep -q "wlan1: <BROADCAST";
then
  echo "Additional WiFi adapter found, configuring for wlan1";
  sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
  sudo iptables -A FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
  sudo iptables -A FORWARD -i wlan0 -o wlan1 -j ACCEPT
else
  echo "No additional WiFi adapter present, configuring for eth0"
  sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
  sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

fi
# store the iptables rules
sudo netfilter-persistent save

sudo sed -i '/^exit 0/i iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

# finally unblock the wlan adapter so that it can be used!
sudo rfkill unblock wlan

echo "************************************"
echo WiFi AP is setup on parent.
echo "************************************"
echo
