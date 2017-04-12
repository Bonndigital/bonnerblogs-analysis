#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Histograms."""
# http://randyzwitch.com/creating-stacked-bar-chart-seaborn/

from scipy import stats
import seaborn as sns
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from os import chdir, path
from sys import path as spath
if True:
    chdir(path.dirname(__file__))
    spath.insert(0, '_robota_install')
    from robota import r_mongo, r_const, r_util, r_date_extractor, r_stats


r_util.log('Setup mongo access..')
col = r_mongo.get_client_for_collection('bonndigital_2017-04-06.full')


def _render_time_graphics():
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


def _render_category_size():
    # QUERY ----------
    q = {r_const.DB_SOURCE_TAGS: {'$ne': None}}
    # ----------------
    values = r_mongo.get_values_from_field_as_list(
        col, q, [r_const.DB_SOURCE_TAGS], cast=lambda x: ' '.join(x))
    #
    # # print(values)
    # domains = [item['__dl_domain'] for item in values]
    # categories = [' '.join(item['__src_tags']).strip() for item in values]
    # # print(categories)
    #
    # # vals = values.values()
    # # print(keys, values)
    r_util.log('Preprocess data..')
    # # print(values)
    df = pd.Series(values)
    # df['0'] = categories
    # df['1'] = domains
    # r_stats.print_pandas_dataframe(df)
    #
    df_plot = df.groupby(df).count().sort_values().plot(kind='barh')
    # print(df_plot.head())
    #
    plt.plot(df_plot.plot())
    plt.xlabel('Anzahl Beiträge', fontsize=14)
    plt.ylabel('BonnerBlogs Kategorie', fontsize=14)
    plt.title('Blogeinträge pro manueller Kategorie', fontsize=14)
    plt.grid(True)
#
    plt.show()

# df.sort_values(inplace=True)

def _render_connection():
    from re import sub
    # QUERY ----------
    q = {r_const.DB_SOURCE_URI: {'$ne': None}}
    # ----------------
    values = r_mongo.get_values_from_field_as_list(
        col, q, [r_const.DB_SOURCE_URI], cast=lambda x: sub(':.*', '', x))
    #
    # # print(values)
    # domains = [item['__dl_domain'] for item in values]
    # categories = [' '.join(item['__src_tags']).strip() for item in values]
    # # print(categories)
    #
    # # vals = values.values()
    # # print(keys, values)
    r_util.log('Preprocess data..')
    # # print(values)
    df = pd.Series(values)

    # df['0'] = categories
    # df['1'] = domains
    r_stats.print_pandas_dataframe(df)
    sns.despine()

    df_plot = df.groupby(df).count().sort_values().plot(kind='pie')
    # print(df_plot.head())
    #
    plt.plot(df_plot.plot())
    # plt.xlabel('Anzahl Beiträge', fontsize=14)
    # plt.ylabel('BonnerBlogs Kategorie', fontsize=14)
    plt.title('Transferprotokolle', fontsize=14)
    plt.grid(True)
# #
    plt.show()


#_render_time_graphics()

# _render_category_size()

_render_connection()
