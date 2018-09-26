#!/bin/sh
#
# This script just tries to make sure that the tornado webserver starts and
# doesn't crash immediately.

! timeout 5 python route.py
