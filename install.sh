#!/bin/bash

cd "$( dirname "$( readlink -f $0 )" )"
robota_dir="_robota_install"
robota_ver="0.1.0"

[ -d $robota_dir ] && exit 0
wget https://github.com/BastiTee/robota/archive/${robota_ver}.zip
unzip ${robota_ver}.zip 
mv robota-${robota_ver} $robota_dir
chmod a+x ${robota_dir}/dev-tools/install.sh
${robota_dir}/dev-tools/install.sh
rm -f ${robota_ver}.zip
