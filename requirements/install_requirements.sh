#!/bin/bash
# shell script to install requirements
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
konsole --noclose -e pip install -r $DIR/requirements.txt
