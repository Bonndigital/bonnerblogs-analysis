#!/bin/bash
# Converts input SQL file to
# 1) csv version of relevant data
# 2) flat list of blog entry links

[ -z "$1" ] && { echo "No input SQL file given."; exit 1; }
in="$( basename $1 .sql )"

echo "-- get sorted raw lines"
tmp1=$( mktemp )
cat ${in}.sql | grep -e "'syndication_source" -e "'syndication_feed" \
-e "'syndication_permalink" |\
sed -r -e "s/^[[:space:]]\([0-9]+,//" -e "s/\),[[:space:]]*$//" \
-e "s/\\\\'/%APOS!%/g" > ${in}.csv # last sed removes apostrophes temporariy

echo "-- extracting permalink list"
cat ${in}.csv |\
grep "syndication_permalink" | tr "," " " | awk '{print $3}' | tr -d "'" |\
sort -u > ${in}.blogentrylinks.txt

wc -l ${in}*
