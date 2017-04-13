#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Histograms."""

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime
import pandas as pd
from os import chdir, path
from sys import path as spath
if True:
    chdir(path.dirname(__file__))
    spath.insert(0, '_robota_install')
    from robota import r_mongo, r_const, r_util, r_date_extractor, r_stats


r_util.log('Setup mongo access..')
col = r_mongo.get_client_for_collection('bonndigital_2017-04-06.full')


def _basic_plot(df_plot, xaxis, yaxis, title):

    sns.despine()
    plt.plot(df_plot.plot())
    plt.xlabel(xaxis, fontsize=14)
    plt.ylabel(yaxis, fontsize=14)
    plt.title(title, fontsize=14)
    plt.grid(True)
    plt.show()


def _render_time_graphics():
    epoch = r_date_extractor.get_current_epoch()
    r_util.log('Current timestamp: {}'.format(epoch))

    r_util.log('Read mongodb data..')
    q = {r_const.DB_DATE_EP: {'$ne': None}}
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

    df_plot = df.groupby(df.dt.month).count().plot(kind='bar')
    _basic_plot(
        df_plot, 'Monat', 'Anzahl Blogartikel',
        'Blogartikel pro Monat')

    df_plot = df.groupby(df.dt.year).count().plot(kind='bar')
    _basic_plot(
        df_plot, 'Jahr', 'Anzahl Blogartikel',
        'Blogartikel pro Jahr')


def _render_category_size():
    q = {r_const.DB_SOURCE_TAGS: {'$ne': None}}
    values = r_mongo.get_values_from_field_as_list(
        col, q, [r_const.DB_SOURCE_TAGS], cast=lambda x: ' '.join(x))

    r_util.log('Preprocess data..')
    df = pd.Series(values)
    df_plot = df.groupby(df).count().sort_values().plot(kind='barh')

    _basic_plot(
        df_plot, 'Anzahl Blogartikel', 'BonnerBlogs Kategorie',
        'Blogartikel je Kategorie')


def _render_connection():
    from re import sub
    q = {r_const.DB_SOURCE_URI: {'$ne': None}}
    values = r_mongo.get_values_from_field_as_list(
        col, q, [r_const.DB_SOURCE_URI], cast=lambda x: sub(':.*', '', x))

    r_util.log('Preprocess data..')
    df = pd.Series(values)
    r_stats.print_pandas_dataframe(df)

    df_plot = df.groupby(df).count().sort_values().plot(kind='pie')

    _basic_plot(df_plot, '', '', 'Transferprotokolle')


_render_time_graphics()

_render_category_size()

_render_connection()
