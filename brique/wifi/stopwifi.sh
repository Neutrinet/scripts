#!/bin/sh
#
# Wrapper script to bring down the wireless interface
# acting as station (see wifiwifi.sh). It stops dhclient and wpa_supplicant
# for that interface, then brings it down with ifconfig.
#
#########################################################################

IW=`sudo ifconfig -a | grep wlan | tail -n1 | cut -d' ' -f1`
echo "[+] Bringing wifi down on $IW..."
PID=`sudo pgrep -f "dhclient $IW"`
sudo kill $PID
PID=`sudo pgrep -f wpa_supplicant`
sudo kill $PID
sudo ifconfig $IW down
echo "[+] Done."
