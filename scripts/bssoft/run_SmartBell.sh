#!/bin/bash

sudo dtoverlay seeed-2mic-voicecard
cd /home/pi/emergency-rp0-2119
sudo alsactl --file ./asound.state restore
sudo -H -u pi /usr/bin/python3 main.py &>> log.txt &
sudo nice -n -20 ./utils/smartbell_mon.sh &>> monlog.txt &
sudo service cron stop
