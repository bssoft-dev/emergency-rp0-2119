#!/bin/bash
echo "------------------------------------"
echo "smartbell_mon.sh is started" 
sleep 3
date
export GW_IP=`ip route show | sed 's/\(\S\+\s\+\)\?default via \(\S\+\).*/\2/p; d'`
echo "Gateway IP is $GW_IP"
if [ ${#GW_IP} -lt 7 ] #If gateway ip was not received properly
then
  echo "Could not find gateway. Rebooting..."
  date
  sudo reboot
fi
export GW_HEAD_IP=${GW_IP:0:6}

# Check smartbell program status
export PROG_STATUS=`ps -ef | grep python | grep -v grep | wc -l`
if [ $PROG_STATUS = 0 ]
then
  echo "Program is not started properly. Rebooting..."
  date
  sudo reboot
fi

# Main loop - Network, program monitoring
while true
do
#  export NET_STATUS=`ping -c 1 $HOST &> /dev/null && echo 1 || echo 0` 
  export NET_STATUS=`ifconfig | grep $GW_HEAD_IP &> /dev/null && echo 1 || echo 0`
  if [ $NET_STATUS = 0 ] # If my ip is unknown 
  then
    echo "Network connection is unstable. Rebooting..."
    date
    sudo reboot
  else
    export PROG_STATUS=`ps -ef | grep python | grep -v grep | wc -l`
    if [ $PROG_STATUS = 0 ] # If program is died
    then
      echo "Smartbell program is died. Start program again."
      date
      sudo -H -u pi /usr/bin/python3 main.py &>> log.txt &
      sleep 10
    else # If every thing is ok
      sleep 10
    fi
  fi
done
