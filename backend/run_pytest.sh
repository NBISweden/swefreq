#!/bin/sh

BROWSER=modules/browser/

py.test . --cov=${BROWSER} --cov-config=modules/browser/tests/.coveragerc

