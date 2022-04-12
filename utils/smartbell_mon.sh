#!/bin/bash
echo "------------------------------------"
echo "smartbell_mon.sh is started" 
date
export GW_IP=`ip route show | sed 's/\(\S\+\s\+\)\?default via \(\S\+\).*/\2/p; d'`
echo "Gateway IP is $GW_IP"

# Check smartbell program status
sleep 1
export PROG_STATUS=`ps -ef | grep python | grep -v grep | wc -l`
if [ $PROG_STATUS = 0 ] # If program is not started properly
then
  echo "Program is not started properly. Rebooting..."
  sudo reboot
fi

# Main loop - Network, program monitoring
while true
do
#  export NET_STATUS=`ping -c 1 $GW_IP &> /dev/null && echo 1 || echo 0` 
  export NET_STATUS=`systemctl is-active ssh.service` 
#  if [ $NET_STATUS = 0 ] # If ping is unreachable 
  if [ $NET_STATUS != "active" ] #network service might be inactive 
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
