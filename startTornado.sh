#!/bin/sh

. /opt/swefreq/venv/bin/activate

cd /opt/swefreq/tornado
python route.py >>log.txt 2>&1 &
