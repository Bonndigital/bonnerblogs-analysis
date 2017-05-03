#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TBD."""

from robota import r_mongo, r_const, r_cmdprs, r_math
from bptbx import b_date

# setup command line parsing --------------------------------------------------
prs = r_cmdprs.init()
r_cmdprs.add_mongo_collection(prs)
args = prs.parse_args()
col = r_cmdprs.check_mongo_collection(prs, args, True)

results = r_mongo.consolidate_mongo_key(
    col, r_const.DB_DATE_EP)
dates = []
for result in results['resultset']:
    if result is None:
        continue
    result = int(result)
    if result < 1356994800 or result >= 1490997600:
        continue
    result = b_date.epoch_to_dto(result)
    result = result.strftime("%Y-%m-%d")
    dates.append(result)

dates = r_math.count_and_sort(dates, remove_outliers=True)
print('date,close')
for date in dates:
    print('{},{}'.format(date[0], date[1]))
