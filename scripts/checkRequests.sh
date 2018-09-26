#!/bin/sh
echo
echo 'Starting time:'
date
. /opt/swefreq/venv/bin/activate
export PYTHONPATH=/opt/swefreq/tornado
python /opt/swefreq/scripts/checkRequests.py
echo
echo '#####################################################################'
