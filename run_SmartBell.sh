#!/bin/bash

sudo dtoverlay seeed-2mic-voicecard
cd /home/pi/emergency-rp0-2119
sudo alsactl --file ./asound.state restore
#nice -n -20 ./RELEASE/run_SmartBell-1.5 $URL "${MAC}" $DURATION $SENSITIVITY
sudo -H -u pi /usr/bin/python3 main.py &
