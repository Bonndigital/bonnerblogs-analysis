#!/bin/bash

cd "$( dirname "$( readlink -f "$0" )" )"
source robota/dev-tools/base.sh
PY=$( get_python_com )
stdoutlog "-- PYTHONVERSION: $( $PY --version )"
export PYTHONPATH=robota:bastis-python-toolbox:${PYTHONPATH}
stdoutlog "-- PYTHONPATH: $PYTHONPATH"

function show_help () {
  [ ! -z "$1" ] && echo "$1"
cat << EOF

Usage: $( basename $0 ) -i [INPUT] [-d]
  -i [INPUT]      Input SQL dump file.
  -d              Force download step
  -e              Force plain text extraction step
EOF
  exit 1
}

while getopts "i:de" opt; do
  case "$opt" in
    i) ifile=$OPTARG;;
    d) forcedl=1;;
    e) forceex=1;;
    *) show_help "Illegal argument.";;
  esac
done
[ -z "$ifile" ] && show_help "Input SQL dump file not set."
[ ! -e "$ifile" ] && show_help "Input SQL dump file does not exist."

ifile=$( sed -r -e "s/\.[^\.]+$//" <<< $ifile )
echo "-- USING FILE: $ifile"

[ ! -f ${ifile}.csv ] && {
    ./prepare-sql-file.sh ${ifile}.sql
} || {
    echo "-- skipped preparing sql file. csv file present."
}

html_dir="_${ifile}-raw-html"
text_dir="_${ifile}-plain-text"
stat_dir="_${ifile}-stats"

#${PY} -m robota_scripts.size_of_mongodb_collection "${ifile}"
size=$( ${PY} -m robota_scripts.size_of_mongodb_collection \
"${ifile}" 2> /dev/null )
echo "-- size of collection '$ifile': $size"
[ -z "$size" ] || [ "$size" == 0 ] && {
    ./write-csv-to-mongodb.py -i ${ifile}.csv
} || {
    echo "-- skipped mongo import. collection present."
}

[ ! -d "$html_dir" ] || [ "$forcedl" == 1 ] && {
    mkdir -p "$html_dir"
    for seq in $( seq 3 )
    do
        find "$html_dir" -type f -size 0 | xargs rm -vf
        ${PY} -m robota_scripts.download_website -c ${ifile} \
        -o "$html_dir" -t 25
    done
} || {
    echo "-- skipped download. folder $html_dir present."
}

[ "$forcedl" == 1 ] && exit

[ ! -d "$text_dir" ] || [ "$forceex" == 1 ] && {
    mkdir -p "$text_dir"
    find "$text_dir" -type f -size 0 | xargs rm -vf
    ${PY} -m robota_scripts.extract_raw_text_from_website -c ${ifile} \
    -i "$html_dir" -o "$text_dir" -t 20
} || {
    echo "-- skipped text extraction. folder $text_dir present."
}

[ "$forceex" == 1 ] && exit

[ ! -f "$stat_dir/lang_det.txt" ] && {
    mkdir -p "$stat_dir"
    ${PY} -m robota_scripts.detect_language -c ${ifile} \
    -i "$text_dir" -o "$stat_dir/lang_det.txt"
} || {
    echo "-- skipped language detection. file $stat_dir/lang_det.txt present."
}

[ ! -f "$stat_dir/date_det.txt" ] && {
    mkdir -p "$stat_dir"
    ${PY} -m robota_scripts.extract_pubdate_from_html -i "$html_dir" \
    -c ${ifile} -o "$stat_dir/date_det.txt"
} || {
    echo "-- skipped date detection. file $stat_dir/date_det.txt present."
}

./get-statistics.py -c ${ifile}
