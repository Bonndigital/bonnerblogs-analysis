#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Histograms."""

from scipy import stats
import seaborn as sns
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from robota import r_mongo, r_const, r_util, r_date_extractor, r_stats


r_util.log('Setup mongo access..')
col = r_mongo.get_client_for_collection('bonndigital_2017-04-06.full')

epoch = r_date_extractor.get_current_epoch()
r_util.log('Current timestamp: {}'.format(epoch))

r_util.log('Read mongodb data..')
# QUERY ----------
q = {r_const.DB_DATE_EP: {'$ne': None}}
# ----------------
dates = r_mongo.get_values_from_field_as_list(
    col, q, [r_const.DB_DATE_EP], cast=lambda x: int(x))


r_util.log('Preprocess data..')
df = pd.Series(dates)
df.sort_values(inplace=True)
df = df[abs(stats.zscore(df)) < 2]  # filter outlier
df = pd.to_datetime(df, unit='s')
df = df.apply(
    lambda df: datetime(year=df.year, month=df.month, day=df.day))
r_stats.print_pandas_dataframe(df)

r_util.log('Prepare plots..')
sns.despine()

df_plot = df.groupby(df.dt.month).count().plot(kind='bar')
plt.plot(df_plot.plot())
plt.xlabel('Monat')
plt.ylabel('Anzahl Blogeinträge')
plt.title('Häufigkeitsverteilung des Veröffentlichungsdatums über Monate')
plt.grid(True)
plt.show()

df_plot = df.groupby(df.dt.year).count().plot(kind='bar')
plt.plot(df_plot.plot())
plt.xlabel('Jahr')
plt.ylabel('Anzahl Blogeinträge')
plt.title('Häufigkeitsverteilung des Veröffentlichungsdatums über Jahre')
plt.grid(True)
plt.show()

print(df.groupby(df.dt.month).count())
