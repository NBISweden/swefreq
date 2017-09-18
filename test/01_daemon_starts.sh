#!/usr/bin/env bash
#
# This script just tries to make sure that the tornado webserver starts and
# doesn't crash immediately.

if timeout 5 python route.py; then
    exit 0
else
    exit 1
fi
