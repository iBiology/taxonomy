#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create a local NCBI Taxonomy (SQLite) Database and query DB with search items.
"""

import os
import sqlite3
import sys
import logging
import tarfile
import tempfile
from collections import defaultdict, namedtuple

try:
    from urllib import urlopen, urlretrieve
except ImportError:
    from urllib.request import urlretrieve

LEVEL = logging.INFO
LOGFILE, LOGFILEMODE = '', 'w'

HANDLERS = [logging.StreamHandler(sys.stdout)]
if LOGFILE:
    HANDLERS.append(logging.FileHandler(filename=LOGFILE, mode=LOGFILEMODE))

logging.basicConfig(format='%(asctime)s %(levelname)-s %(name)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', handlers=HANDLERS, level=LEVEL)

logger = logging.getLogger('[taxonomy]')
warn, info, error = logger.warning, logger.info, logger.error

DB = os.path.join(os.path.expanduser('~'), '.NCBITaxonomy.sqlite')


def download():
    url = 'https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'
    dump = os.path.join(os.path.expanduser('~'), '.taxdump.tar.gz')
    try:
        urlretrieve(url, dump)
        assert os.path.isfile(dump), 'Download taxdump.tar.gz failed!'
    except Exception:
        error('Download taxdump.tar.gz failed, check your internet connection.')
        if os.path.isfile(dump):
            os.remove(dump)
        sys.exit(1)
    return dump


def parse(dump):
    with tarfile.open(dump) as tar:
        info('\tParsing names (names.dmp) ...')
        scientifics, commons, synonyms, others = [], [], [], []
        for line in tar.extractfile('names.dmp'):
            taxid, name, _, name_class, _ = [field.strip() for field in
                                             str(line.decode()).split('|')]
            if name_class == 'scientific name':
                scientifics.append([taxid, name])
            elif name_class in 'genbank common name':
                commons.append([taxid, name])
            elif name_class in 'genbank synonym':
                synonyms.append([taxid, name])
            else:
                others.append([taxid, name])
        
        info('\tParsing merged ids (merged.dmp) ...')
        merged = [str(line.decode()).replace('\t|\n', '').split('\t|\t') for
                  line in tar.extractfile('merged.dmp')]
        
        info('\tParsing nodes (nodes.dmp) ...')
        nodes = [str(line.decode()).split('\t|\t')[:3] for line in
                 tar.extractfile('nodes.dmp')]
    return scientifics, commons, synonyms, others, merged, nodes


def taxdump():
    info('Downloading taxdump (taxdump.tar.gz) from NCBI FTP site (via HTTP).')
    dump = download()
    
    try:
        info('Download successfully! Parsing taxdump ...')
        scientifics, commons, synonyms, others, merged, nodes = parse(dump)
    finally:
        os.remove(dump)
    return scientifics, commons, synonyms, others, merged, nodes


def md5():
    url = 'https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz.md5'
    return urlopen(url).read().split()[0]


def upload(conn, md, scientifics, commons, synonyms, others, merged, nodes):
    info('\tUploading md5 ...')
    conn.execute('INSERT INTO md5 (md5) VALUES (?);', (md, ))
    info('\tUploading scientific names ...')
    conn.executemany('INSERT INTO scientifics (taxid, sname) VALUES (?, ?);',
                     [(int(taxid), name) for taxid, name in scientifics])
    info('\tUploading common names ...')
    conn.executemany('INSERT INTO commons (taxid, cname) VALUES (?, ?);',
                     [(int(taxid), name) for taxid, name in commons])
    info('\tUploading synonym names ...')
    conn.executemany('INSERT INTO synonyms (taxid, syname) VALUES (?, ?);',
                     [(int(taxid), name) for taxid, name in synonyms])
    info('\tUploading other names ...')
    conn.executemany('INSERT INTO others (taxid, oname) VALUES (?, ?);',
                     [(int(taxid), name) for taxid, name in others])
    info('\tUploading merged taxa IDs ...')
    conn.executemany('INSERT INTO merged (old, new) VALUES (?, ?);',
                     [(int(old), int(new)) for old, new in merged])
    info('\tUploading nodes ...')
    conn.executemany('INSERT INTO nodes (taxid, parent, rank) VALUES (?, ?, ?);',
                     [(int(taxid), int(parent), rank)
                      for taxid, parent, rank in
                      nodes])
    conn.commit()
    
    
def drop_table(conn):
    conn.execute('DROP TABLE IF EXISTS md5;')
    conn.execute('DROP TABLE IF EXISTS scientifics;')
    conn.execute('DROP TABLE IF EXISTS commons;')
    conn.execute('DROP TABLE IF EXISTS synonyms;')
    conn.execute('DROP TABLE IF EXISTS others;')
    conn.execute('DROP TABLE IF EXISTS merged;')
    conn.execute('DROP TABLE IF EXISTS nodes;')


def create_table(conn):
    conn.execute('CREATE TABLE md5 (md5 TEXT);')
    conn.execute('CREATE TABLE scientifics (taxid INT, sname TEXT);')
    conn.execute('CREATE TABLE commons (taxid INT, cname TEXT);')
    conn.execute('CREATE TABLE synonyms (taxid INT, syname TEXT);')
    conn.execute('CREATE TABLE others (taxid INT, oname TEXT);')
    conn.execute('CREATE TABLE merged (old INT PRIMARY KEY, new INT);')
    conn.execute('CREATE TABLE nodes (taxid INT, parent INT, rank TEXT);')
    
    
def update(conn, md):
    record = conn.execute('SELECT md5 FROM md5;').fetchone()
    s = record[0] if record else ''
    
    if s != md:
        info('Local DB was outdated, updating ...')
        data = taxdump()
        
        info('Dropping old tables ...')
        drop_table(conn)
        
        info('Creating new tables ...')
        create_table(conn)
        
        upload(conn, md, *data)
        info('Successfully updated local SQLite database.')
    else:
        info('Local SQLite database already up to date, update skipped.')


def database(db):
    md = md5()
    if os.path.isfile(db):
        info('Connecting to local NCBI Taxonomy Database ...')
        conn = sqlite3.connect(db)
        update(conn, md)
    else:
        info('Retrieving data from NCBI Taxonomy to create local database.')
        data = taxdump()
        
        info('Creating local database {} ...'.format(db))
        conn = sqlite3.connect(db)
        
        info('Creating tables ...')
        create_table(conn)
        
        info('Uploading data to tables ...')
        upload(conn, md, *data)
        
        info('Successfully create local NCBI Taxonomy SQLite Database.')
        info('Local Database was saved to: {}.'.format(db))
    return conn


def id2id(db, taxid):
    r = db.execute('SELECT new FROM merged WHERE old = ?;', (int(taxid), ))
    return r.fetchone()[0] if r.fetchone() else int(taxid)


def name2id(db, name):
    taxid, scientific, common = None, '', ''
    name = name.lower()
    r = db.execute('SELECT taxid FROM scientifics '
                   'WHERE LOWER(sname) = ? LIMIT 1;', (name, )).fetchone()
    if r:
        taxid = r[0]
    else:
        r = db.execute('SELECT taxid FROM commons '
                       'WHERE LOWER(cname) = ? LIMIT 1;', (name, )).fetchone()
        if r:
            taxid = r[0]
        else:
            r = db.execute('SELECT taxid FROM  synonyms '
                           'WHERE LOWER(syname) = ? LIMIT 1;',
                           (name, )).fetchone()
            if r:
                taxid = r[0]
            else:
                r = db.execute('SELECT taxid FROM  others '
                               'WHERE LOWER(oname) = ? LIMIT 1;',
                               (name, )).fetchone()
                if r:
                    taxid = r[0]
    return taxid


def id2name(db, taxid):
    scientific, common = '', ''
    if taxid:
        taxid = id2id(db, taxid)
        r = db.execute('SELECT sname FROM scientifics WHERE taxid = ? LIMIT 1;',
                       (taxid, )).fetchone()
        if r:
            scientific = r[0]
            r = db.execute('SELECT cname FROM commons '
                           'WHERE taxid = ?;', (taxid, )).fetchall()
            if r:
                common = ', '.join(r[0])
    return taxid, scientific, common


def get_parent_rank(db, taxid):
    parent, rank = None, ''
    r = db.execute('SELECT parent, rank FROM nodes '
                   'WHERE taxid = ? LIMIT 1;', (taxid, )).fetchone()
    if r:
        parent, rank = r
    return parent, rank


def get_lineage(db, taxid, lineages):
    rank, lineage = '', []
    while 1:
        p, r = get_parent_rank(db, taxid)
        if not rank:
            rank = r
        if not lineages:
            break
        if p != 1:
            lineage.append(p)
            taxid = p
        else:
            break
    if lineage:
        lineage = [id2name(db, i) for i in lineage]
        lineage = [{'TaxId': i[0], 'ScientificName': i[1]} for i in lineage]
    return rank, lineage


def search(data, lineages):
    taxa = []
    db = database(DB)
    try:
        info('Searching in local NCBI Taxonomy database')
        for d in data:
            if d.isdigit():
                info('\tSearching names for taxon {}'.format(d))
                taxid, scientific, common = id2name(db, d)
            else:
                info('\tSearching taxon ID for taxon {} ...'.format(d))
                taxid = name2id(db, d)
                taxid, scientific, common = id2name(db, taxid)
            if taxid:
                rank, lineage = get_lineage(db, taxid, lineages)
            else:
                rank, lineage = '', []
            record = [taxid, scientific, common, rank, lineage]
            if any(record):
                info('\tSummarizing search results for taxon {}'.format(d))
                taxa.append(record)
            else:
                info('\tNo record found for taxon {}.'.format(d))
    finally:
        db.close()
    return taxa
            
    
if __name__ == '__main__':
    pass
