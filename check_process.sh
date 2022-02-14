#!/bin/sh

cd `dirname $0`
PROCESS_NAME="python3 main.py"

count=`pgrep -f "${PROCESS_NAME}" | wc -l`
if [ $count = 0 ]; then
    DATE=`date '+%Y-%m-%d %H:%M:%S'`
    echo "$DATE '${PROCESS_NAME}' is stop" >> check_process_log.log

    $PROCESS_NAME &

    echo "$DATE '${PROCESS_NAME}' is start" >> check_process_log.log
fi

exit