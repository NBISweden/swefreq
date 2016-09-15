#!/bin/bash

# Stops the ExAC browser.

if [ $( id -u ) -ne 0 ]; then
	echo "Please run this as the root user" >&2
	exit 1
fi

pkill -f 'python exac.py --host=0.0.0.0'
