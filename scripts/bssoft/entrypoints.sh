#!/bin/bash

if [ $1 = "start" ]
then
  cd /home/bssoft/emergency-rp0-2119
  ./run.sh
  ./utils/smartbell_mon.sh &>> /home/bssoft/emergency-rp0-2119/logs/monlog.txt &
else
  pkill -9 smartbell
  pkill -9 python
fi
