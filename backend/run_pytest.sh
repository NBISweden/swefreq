#!/bin/sh

BROWSER=modules/browser/

py.test . --cov=${BROWSER}
