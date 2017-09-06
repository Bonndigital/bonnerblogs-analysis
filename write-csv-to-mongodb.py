#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read CSV file and write content to MongoDB."""

from os import chdir, path
from sys import path as spath
import csv
from bptbx import b_iotools
from re import sub
if True:
    chdir(path.dirname(__file__))
    spath.insert(0, '_robota_install')
    from robota import r_mongo, r_const, r_util
    from bptbx import b_cmdprs

# setup command line parsing
prs = b_cmdprs.init()
b_cmdprs.add_file_in(prs)
args = prs.parse_args()
b_cmdprs.check_file_in(prs, args)

# setup mongodb connection
bname = b_iotools.basename(args.i, '.csv')
col = r_mongo.get_client_for_collection(bname)
print('-- size of collection: {}'.format(r_mongo.get_collection_size(col)))
r_mongo.clear_collection(col)
print('-- size of collection: {}'.format(r_mongo.get_collection_size(col)))

# dump data into mongodb
with open(args.i, 'rt') as csvfile:
    csv_datasets = csv.reader(csvfile,
                              delimiter=',', quotechar='\'')

    for csv_dataset in csv_datasets:
        source_id = csv_dataset[0]
        doc = r_mongo.get_doc_or_none(col, '_id', source_id)
        if not doc:
            doc = {
                '_id': source_id,  # only temporary
                'sql_source_id': source_id
            }
            r_mongo.insert_doc(col, doc)
        # remove some noise
        csv_dataset[2] = sub('^BonnerBlogs\.de - ', '', csv_dataset[2])
        csv_dataset[2] = sub('\);$', '', csv_dataset[2])
        # bring back apostrophes
        csv_dataset[2] = sub('%APOS!%', '\'', csv_dataset[2])
        # replace keys of some common fields
        key = csv_dataset[1]
        key = sub('^syndication_', '', key)
        key = sub('^permalink$', r_const.DB_SOURCE_URI, key)
        key = sub('^source$', r_const.DB_SOURCE_TAGS, key)
        key = sub('^source_original$', r_const.DB_SOURCE_COLL, key)
        if key is r_const.DB_SOURCE_TAGS:
            doc[key] = [csv_dataset[2]]
        else:
            doc[key] = csv_dataset[2]
        r_mongo.replace_doc(col, doc)
csvfile.close()

# remove duplicate or empty permalinks
permas = []
print('-- size of collection: {}'.format(r_mongo.get_collection_size(col)))
for doc in r_mongo.get_snapshot_cursor(col):
    perma = None
    try:
        perma = doc[r_const.DB_SOURCE_URI]
    except KeyError:
        pass
    if perma in permas or not perma:
        r_mongo.delete_doc(col, doc)
        continue
    else:
        permas.append(perma)

# replace key with id from permalink
r_mongo.get_collection_size(col)
for doc in r_mongo.get_snapshot_cursor(col):
    new_key, _ = r_util.get_key_from_url(doc[r_const.DB_SOURCE_URI])
    r_mongo.change_id(col, doc, new_key)

# fin
print('-- size of collection: {}'.format(r_mongo.get_collection_size(col)))
