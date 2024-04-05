#!/bin/bash

if [ $1 = "start" ]
then
  cd /home/bssoft/emergency-rp0-2119
  ./run.sh
else
  pkill -9 python
fi
