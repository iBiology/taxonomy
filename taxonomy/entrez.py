#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search NCBI Taxonomy Database with Entrez Programming Utilities (Bio.Entrez).
"""


import sys
import logging

LEVEL = logging.INFO
LOGFILE, LOGFILEMODE = '', 'w'

HANDLERS = [logging.StreamHandler(sys.stdout)]
if LOGFILE:
    HANDLERS.append(logging.FileHandler(filename=LOGFILE, mode=LOGFILEMODE))

logging.basicConfig(format='%(asctime)s %(levelname)-s %(name)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', handlers=HANDLERS, level=LEVEL)

logger = logging.getLogger('[taxonomy]')
warn, info, error = logger.warning, logger.info, logger.error

try:
    from Bio import Entrez
except ImportError:
    error('Biopython not installed. Please consider one of the followings:'
          '\n\t1. install biopython.'
          '\n\t2. remove "-e" flag and the email address.')
    sys.exit()


def ids2names(ids):
    taxa = []
    handle = Entrez.efetch('taxonomy', id=','.join(ids))
    records = Entrez.read(handle)
    for r in records:
        taxid = r.get('TaxId', None)
        scientific = r.get('ScientificName', '')
        common = r.get('OtherNames', {}).get('GenbankCommonName', '')
        rank = r.get('Rank', '')
        lineage = r.get('LineageEx', [])
        taxa.append([taxid, scientific, common, rank, lineage])
    return taxa


def name2id(name):
    handle = Entrez.esearch('taxonomy', term=name)
    records = Entrez.read(handle)
    return records['IdList']
        
        
def search(data, email):
    info('Searching via Entrez Programming Utilities')
    Entrez.email = email

    ids, taxa = [], []
    for d in data:
        if d:
            if d.isdigit() or isinstance(d, int):
                ids.append(str(d))
            else:
                ids.extend(name2id(d))
    
    return ids2names(ids)
    
    
if __name__ == '__main__':
    pass
