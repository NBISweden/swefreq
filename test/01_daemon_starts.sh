#!/usr/bin/env bash
#
# This script just tries to make sure that the tornado webserver starts and
# doesn't crash immediately.

python route.py &
pid=$!

# sleep for 5 seconds
for i in {1..5}; do
    sleep 1
    if ! kill -0 $pid; then
        exit 1
    fi
done

kill $pid
wait $pid
exit 0
