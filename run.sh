#!/bin/bash
export VIRTUALENV_ACTIVATOR_SIMPLE=1
. /home/protected/server/venv/etc/activate.sh
exec python3 server.py

