#!/bin/bash

pid=`ps -ef|grep "python server.py"|grep -v "grep"|awk '{print $2}'`

if [ ! "$pid" ];then
        echo "no flask process need to kill"
else
        echo "kill flask process [$pid] start"
        kill -9 $pid
        echo "kill flask process [$pid] end"
fi
cd ..
source venv/bin/activate
nohup python server.py 2100 &
nohup python server.py 2101 &