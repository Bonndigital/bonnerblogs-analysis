#!/bin/bash

bname="bonndigital_2017-04-06.sanity"
find . -maxdepth 1 -iname "*${bname}*" | grep -v -e "^.*\.sql$" | xargs rm -rfv
mongo robota --eval "db['$bname'].drop()"
