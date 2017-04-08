#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtain interesting statistics from given dataset."""

from os import chdir, path
from sys import path as spath
if True:
    chdir(path.dirname(__file__))
    spath.insert(0, '_robota_install')
    from robota import r_util, r_mongo, r_const, r_cmdprs

# setup command line parsing --------------------------------------------------
prs = r_cmdprs.init()
r_cmdprs.add_mongo_collection(prs)
args = prs.parse_args()
col = r_cmdprs.check_mongo_collection(prs, args, True)

# run analysis ----------------------------------------------------------------

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(col, r_const.DB_SOURCE_TAGS),
    'Manual categories', print_counter_stats=True)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(col, r_const.DB_SOURCE_COLL),
    'Blogs', counter_max=25)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(col, r_const.DB_DL_DOMAIN),
    'Domains', counter_max=25)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_SOURCE_URI,
        if_filter=lambda x: x.startswith('https:')),
    'Blogeinträge (HTTPS)', print_counter=False)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_SOURCE_URI, if_filter=lambda x: x.startswith('http:')),
    'Blogeinträge (HTTP)', print_counter=False)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(col, r_const.DB_DL_RESCODE),
    'HTTP-Response')

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(col, r_const.DB_DL_RAWFILESIZE),
    'HTML-Größe', print_counter=False, print_resultset_stats=True)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_DL_ERROR, process_value=lambda x: str(x)[0:75]),
    'Download-Fehler', print_counter=True, counter_max=25,
    print_resultset_stats=False, )

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_TE_WC),
    'Textlänge in Wörtern', print_counter=False, print_resultset_stats=True)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_LANG_AUTO),
    'Sprachen', print_counter=True)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_DATE_EP),
    'Zeiten', print_counter=False, print_counter_stats=False,
    print_resultset_stats=True)

r_util.print_result_statistics(
    r_mongo.consolidate_mongo_key(
        col, r_const.DB_DATE_HINT),
    'Zeitquelle', print_counter=True)


r_util.log('\n+++ DATEN ÜBERBLICK +++', color='green')
t = []
t.append(['total', r_mongo.count_docs(
    col, {}
)])
t.append(['german', r_mongo.count_docs(
    col, {r_const.DB_LANG_AUTO: {'$eq': 'de'}}
)])
t.append(['german-20+tokens', r_mongo.count_docs(
    col, {r_const.DB_TE_WC: {'$gt': 20}, r_const.DB_LANG_AUTO: {'$eq': 'de'}}
)])
t.append(['date-found', r_mongo.count_docs(
    col, {r_const.DB_DATE_EP: {'$ne': None}}
)])

r_util.print_table(t, headers=['date', 'count'])
