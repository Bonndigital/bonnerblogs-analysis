#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TBD."""

from robota import r_mongo, r_const, r_math
from bptbx import b_date, b_cmdprs

# setup command line parsing --------------------------------------------------
prs = b_cmdprs.init()
b_cmdprs.add_mongo_collection(prs)
args = prs.parse_args()
col = b_cmdprs.check_mongo_collection(prs, args, True)

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

dates = r_math.count_and_sort(dates, reject_outliers=True, outliers_m=2)
print('date,close')
for date in dates:
    print('{},{}'.format(date[0], date[1]))
