#!/bin/bash

# PREREQUISITES ---------------------------------------------------------------

for tool in node npm unfluff jq sed awk curl cat shuf find; do
    [ -z $( command -v $tool ) ] && {
        missing="$tool $missing"
    }
done
[ ! -z $missing ] && { echo "Required tool(s) '$missing' not installed."; \
exit 1; }

# CONSTANTS / CMDLINE ---------------------------------------------------------

SANITY=1
MAX_THREADS=50

function show_help () {
[ ! -z "$1" ] && echo -e "$1\n"
cat << EOF
Usage: $( basename $0) -i <SQL-DUMP> [-f] [-t <THREADS>]

  -i <SQL-DUMP>  Input bonn-digital sql dump
  -f             Full data processing (will run a sanity check by default)
  -t <THREADS>   Maximum threads (default: $MAX_THREADS)

EOF
exit 1
}

# parse cmd line
while getopts "hi:t:f" opt; do
    case "$opt" in
    i) RAW_INPUT="$OPTARG";;
	t) MAX_THREADS="$OPTARG";;
    f) SANITY=0;;
	h) show_help;;
	*) echo "Illegal argument."; show_help;;
	esac
done
[ -z "$RAW_INPUT" ] && show_help "Input file not set."
[ ! -f "$RAW_INPUT" ] && show_help "Input file does not exist."
echo "-- using $MAX_THREADS threads; sanity=$SANITY; file=$RAW_INPUT"

# HELPER FUNCTIONS ------------------------------------------------------------

function check_http_code () {
	# extracts the http status code for a given URL
	[ -z "$1" ] && return
	echo "$( curl -sL -w "%{http_code}\\n" "$1" -o /dev/null ) $1"
}

function metadata_extraction () {
	[ -z "$1" ] && return
	raw_fname="$( sed -r -e "s/[^a-zA-Z0-9_-]+/_/g" <<< "$1" )"
	raw_fname="${raw_fname:0:100}.json" # truncate filename
	dirn="json-raw/${raw_fname:0:25}"
	mkdir -p $dirn
	raw_fname="${dirn}/${raw_fname}"
	[ ! -f $raw_fname ] && { # don't rewrite existing data
		curl -m 10 -s "$1" | unfluff > $raw_fname
		echo "   + $raw_fname"
	}

}

function fulltext_extraction () {
	[ -z "$1" ] && return
	raw_fname="$( basename "$1" .json ).txt"
	dirn="fulltext-raw/${raw_fname:0:25}"
	mkdir -p $dirn
	raw_fname="${dirn}/${raw_fname}"
	created=0
	[ ! -f $raw_fname ] && { # don't rewrite existing data
		cat "$1" | jq -r .title
		cat "$1" | jq -r .description
		cat "$1" | jq -r .text
		created=1
	} > $raw_fname
	[ $created == 1 ] && echo "   + $raw_fname"
}

# export for usage with xargs
export -f check_http_code
export -f metadata_extraction
export -f fulltext_extraction

# MAIN PROCESS ----------------------------------------------------------------

# You can activate full data mode by using the "--real" cmdline toggle
[ "$1" == "--real" ] && SANITY=0

# switch to either sanity or fulldata mode
[ ! -z "$SANITY" ] && [ $SANITY == 1 ] && {
	echo "-- switching to sanity mode"
	# cleanup last sanity run
	rm -rf "_sanity" && mkdir -p "_sanity"
	# create a randomized reduces SQL input set that will produce
	# approx. 25-75 permalinks in the following process
	shuf $RAW_INPUT | head -n250 > _sanity/$RAW_INPUT
	cd "_sanity"
	echo "-- now in working dir $( pwd )"
} || {
	echo "-- switching to real-data mode"
	mkdir -p "_full_parse"
	cd "_full_parse"
	RAW_INPUT="../$RAW_INPUT"
	echo "-- now in working dir $( pwd )"
}

[ ! -f 001-all-links.txt ] && {
	echo "-- extracting all permalinks from sql dump"
	cat $RAW_INPUT | grep syndication_permalink |\
	tr "," " " | tr "'" " " | awk '{print $4}' | sort | uniq \
	> 001-all-links.txt
} || {
	echo "-- skipped permalink extraction. output file exists."
}

[ ! -f 002-httpcodes-links.txt ] && {
	echo "-- checking page availability"
	cat 001-all-links.txt \
	| xargs -n 1 -P $MAX_THREADS -I {} bash -c 'check_http_code "$@"' _ {} \
	> 002-httpcodes-links.txt
} || {
	echo "-- skipped page availability check. output file exists."
}

[ ! -f 003-http-200-links.txt ] && {
	echo "-- filter available pages"
	cat 002-httpcodes-links.txt | grep -e "^2.*" | awk '{print $2}' \
	> 003-http-200-links.txt
} || {
	echo "-- skipped filter available pages. output file exists."
}

echo "-- remove any 0-byte file from a previous run"
mkdir -p "json-raw"
mkdir -p "fulltext-raw"
find "json-raw" -size 0 | xargs rm 2> /dev/null
find "fulltext-raw" -size 0 | xargs rm 2> /dev/null

echo "-- dumping main content from blogs to json files"
cat 003-http-200-links.txt | xargs -n 1 -P $MAX_THREADS -I {} \
bash -c 'metadata_extraction "$@"' _ {}

echo "-- dumping fulltext content to plain text files"
find json-raw -type f  | xargs -n 1 -P $MAX_THREADS -I {} \
bash -c 'fulltext_extraction "$@"' _ {}

# ---- to be continued
