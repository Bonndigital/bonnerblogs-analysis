#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Some basic graphic rendering done with seaborn."""

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
from robota import r_mongo, r_const, r_date_extractor
from bptbx import b_cmdprs

# setup command line parsing --------------------------------------------------
prs = b_cmdprs.init()
b_cmdprs.add_mongo_collection(prs)
args = prs.parse_args()
col = b_cmdprs.check_mongo_collection(prs, args, True)


def _basic_plot(df_plot, xaxis, yaxis, title):

    sns.despine()
    plt.plot(df_plot.plot())
    plt.xlabel(xaxis, fontsize=14)
    plt.ylabel(yaxis, fontsize=14)
    plt.title(title, fontsize=14)
    plt.grid(True)
    plt.show()


epoch = r_date_extractor.get_current_epoch()
# r_util.log('Current timestamp: {}'.format(epoch))
#
# r_util.log('Read mongodb data..')
q = {r_const.DB_DATE_EP: {'$ne': None}}
dates = r_mongo.get_values_from_field_as_list(
    col, q, [r_const.DB_DATE_EP], cast=lambda x: int(x))

# r_util.log('Preprocess data..')
df = pd.Series(dates)
df.sort_values(inplace=True)
df = df[abs(stats.zscore(df)) < 2]  # filter outlier
df = pd.to_datetime(df, unit='s')
# df = df.apply(
#     lambda df: datetime(year=df.year, month=df.month, day=df.day))
# r_stats.print_pandas_dataframe(df)
with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
    print(df)
