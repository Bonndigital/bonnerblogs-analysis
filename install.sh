#!/bin/bash

cd "$( dirname "$( readlink -f $0 )" )"
robota_dir="_robota_install"

[ ! -d $robota_dir ] && git clone https://github.com/BastiTee/bastis-data-analysis-toolbox.git $robota_dir
chmod a+x ${robota_dir}/dev-tools/install.sh
${robota_dir}/dev-tools/install.sh
