#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TBD."""

from collections import Counter
from robota import r_mongo, r_const
from bptbx import b_date, b_cmdprs
import json
from re import sub

# setup command line parsing --------------------------------------------------
prs = b_cmdprs.init()
b_cmdprs.add_mongo_collection(prs)
args = prs.parse_args()
col = b_cmdprs.check_mongo_collection(prs, args, True)

# get top 25 blogs
results = r_mongo.consolidate_mongo_key(col, r_const.DB_SOURCE_COLL)
top_blogs = {}
for tuple in results['counter'].most_common(50):
    top_blogs[tuple[0]] = {}
    top_blogs[tuple[0]]['total_art'] = tuple[1]


def _if_filter(x): return x is not None and x >= 1388530800  # 01.01.2014


for blog in top_blogs.keys():
    results = r_mongo.consolidate_mongo_key(
        col, r_const.DB_DATE_EP, if_filter=_if_filter,
        query={"__src_collection": {"$eq": blog}})
    top_blogs[blog]['timestamps'] = results['resultset']
    top_blogs[blog]['with_date'] = results['resultset_stats']['len']
    top_blogs[blog]['date_perc'] = float(
        top_blogs[blog]['with_date']) / float(top_blogs[blog]['total_art'])

top_blogs_sel = {}
# drop some candidates
for blog in top_blogs.keys():
    cblog = top_blogs[blog]
    if (int(cblog['with_date'] > 300) and
            float(cblog['date_perc']) >= 0.8):
        top_blogs_sel[blog] = cblog
    else:
        from sys import stderr
        print('{} skipped [tot={} wdate={} perc={}]'.format(
            blog, cblog['total_art'], cblog['with_date'],
            cblog['date_perc']), file=stderr)

# create date-histograms
for blog in top_blogs_sel.keys():
    top_blogs[blog]['timestamps'] = (
        [b_date.epoch_to_dto(x).strftime('%Y-%m')
         for x in top_blogs[blog]['timestamps'] if x is not None])
    top_blogs[blog]['timestamps'] = Counter(top_blogs[blog]['timestamps'])

# print result format
result_data = []
for blog in top_blogs_sel.keys():
    dataset = {}
    dataset['total'] = top_blogs[blog]['total_art']
    dataset['name'] = sub('&amp;', '&', blog)
    ts = []
    for key in top_blogs[blog]['timestamps']:
        if "2017" in key:  # skip current year
            continue
        ts_set = [key, top_blogs[blog]['timestamps'][key]]
        ts.append(ts_set)
    dataset['articles'] = ts
    result_data.append(dataset)
print(json.dumps(result_data, sort_keys=True, indent=4))
