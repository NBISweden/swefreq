#!/bin/bash
echo
echo "Starting time:"
date
source /opt/swefreq/venv/bin/activate
python /opt/swefreq/tornado/checkForNewUsers.py
echo
echo "#####################################################################"
