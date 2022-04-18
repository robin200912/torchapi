#!/bin/bash

set -e
echo "start..."
pid=$(ps -x | grep app.py | grep -v 'grep' | awk '{print $1}')
echo $pid
if [ -n "$pid" ]; then
  kill -9 $pid
fi

nohup python app.py >"logs/api.log" 2>&1 &
echo "end..."