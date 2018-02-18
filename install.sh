#!/bin/bash

cd "$( dirname "$( readlink -f "$0" )" )"
git submodule init
git submodule update
chmod a+x robota/dev-tools/install.sh
robota/dev-tools/install.sh
source robota/dev-tools/base.sh
PY=$( get_python_com )
export PYTHONPATH=${PYTHONPATH}:robota:bastis-python-toolbox
$PY robota/robota_test/test_suite.py
