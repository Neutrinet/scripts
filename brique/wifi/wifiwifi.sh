#!/bin/bash
# Simple script to get uplink connectivity over WiFi using wpa_supplicant.
# You'll need two wireless interfaces for this script to work.
#
# Default interface (wlan0) acts as access point (hotspot in yunohost lingo),
# the second one you plug will act as a client.
# If you already have an Internet Cube from Neutrinet, just plug an additional 
# wireless adapter and run the script. This should work out of the box.
#
# Potential additions:
#   * use iw scan to check that we receive beacons for $SSID
#   * pull VPN concentrator hostname from device's config ?
#   * check wireless association status with wpa_cli instead of sleeping ?
#   * length check on PSK ?
#
###############################################################################

if [ $# -ne 2 ]; then
	echo "Usage: $0 SSID PSK";
	exit -1
fi
SSID=$1
PSK=$2

# get the latest wireless interface and brings it up
IW=`sudo ifconfig -a | grep wlan | tail -n1 | cut -d' ' -f1`
echo "[+] Bringin $IW up..."
sudo ifconfig $IW up 1>/dev/null

# create wpa_supplicant config, launch wpa_supplicant, wait for association
# then get a DHCP lease (DHCP is how most general public routers work, if 
# you tinkered with fixed IPs, you should be able to modify this script by
# yourself).
echo "[+] Creating wpa_supplicant setting ..."
sudo wpa_passphrase $SSID $PSK | sudo tee /etc/wpa_supplicant/wifi.txt 1>/dev/null
echo "[+] Launching wpa_supplicant..."
sudo wpa_supplicant -i $IW -c /etc/wpa_supplicant/wifi.txt -B 1>/dev/null
sleep 2
echo "[+] We should be associated by now. Requesting DHCP lease..."
sudo dhclient $IW 1>/dev/null
if [ $? -eq 2 ]; then
	echo "[+] Failed to get a lease. Aborting."
	PID=`sudo pgrep -f "dhclient $IW"`
	sudo kill $PID
	PID=`sudo pgrep -f wpa_supplicant`
	sudo kill $PID
	sudo ifconfig $IW down		
	exit -1
fi

# we get the default gateway by appending ".1" to our assigned IP. Once
# again, that's how most general public routers work (/24 subnet with .1 acting
# as the gateway).
GW=$(echo `sudo route -nee | grep $IW | cut -d' ' -f1 | cut -d'.' -f1,2,3`.1)
echo "[+] DHCP lease acquired. Setting up routes with gateway $GW ..."

# Rely on route metrics so we don't cut our current connection when doing
# this over SSH within a VPN tunnel. Yes, that happened...
VPN_CONCENTRATOR_IP=`host vpn.neutrinet.be | grep "has address" | cut -d' ' -f4`
sudo ip ro add default dev $IW via $GW metric 100
sudo ip ro add $VPN_CONCENTRATOR_IP via $GW dev $IW metric 100

# at this point you can unplug the Ethernet cable and traffic will flow through
# the air like it just don't care ! 
echo "[+] All done. Enjoy your wireless Interwebz!"
