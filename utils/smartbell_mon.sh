#!/bin/bash
echo "------------------------------------"
echo "smartbell_mon.sh is started" 
date
export GW_IP=`ip route show | sed 's/\(\S\+\s\+\)\?default via \(\S\+\).*/\2/p; d'`
echo "Gateway IP is $GW_IP"

# Check smartbell program status
sleep 1
export PROG_STATUS=`ps -ef | grep python | wc -l`
if [ $PROG_STATUS = 0 ] # If program is not started properly
then
  echo "Program is not started properly. Rebooting..."
  sudo reboot
fi

# Main loop - Network, program monitoring
while true
do
  export NET_STATUS=`ping -c 1 $GW_IP &> /dev/null && echo 1 || echo 0` 
  if [ $NET_STATUS = 0 ] # If ping is unreachable 
  then
    echo "Network connection is unstable. Rebooting..."
    date
    sudo reboot
  else
    export LAST_MESSAGE=`tail -1 logs/smartbell.log | awk '{print$8}'`
    if [[ $LAST_MESSAGE = "overflowed" ]] # If program is died
    then
      echo "Smartbell program is died. Start program again."
      date
      sudo -H -u pi /usr/bin/python3 main.py &>> log.txt &
      sleep 5
    else # If every thing is ok
      sleep 5
    fi
  fi
done
