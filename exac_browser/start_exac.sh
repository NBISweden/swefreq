#!/bin/bash

# Starts the ExAC browser.
# Logs to exac_browser.log (not rotated).

if [ $( id -u ) -ne 0 ]; then
	echo "Please run this as the root user" >&2
	exit 1
fi

source exac_env/bin/activate
nohup python exac.py --host=0.0.0.0 >exac_browser.log 2>&1 &
