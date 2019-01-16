#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command line tool searching taxonomy information from NCBI Taxonomy Database.
"""

import argparse
import sys
import logging

import entrez
import database

LEVEL = logging.INFO
LOGFILE, LOGFILEMODE = '', 'w'

HANDLERS = [logging.StreamHandler(sys.stdout)]
if LOGFILE:
    HANDLERS.append(logging.FileHandler(filename=LOGFILE, mode=LOGFILEMODE))

logging.basicConfig(format='%(asctime)s %(levelname)-s %(name)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', handlers=HANDLERS, level=LEVEL)

logger = logging.getLogger('[taxonomy]')
warn, info, error = logger.warning, logger.info, logger.error

ITEM_HELP = """Search item. The item can be a single taxon name
(either scientific or common name) or a taxon ID.
The search can also be a set of items separated
by comma (,) mixing of names or taxon IDs, e.g.,

  human            - A single common name
  Homo sapiens     - A single scientific name
  human,Bos taurus - A mix of common name and taxon ID
  human,Bos taurus - A mix of common and scientific names
  9606,Bos taurus  - A mix of taxon ID and scientific name
  
Multiple search items must to be separated by commas.
Names contained in search item are case insensitive.
Spaces in names need to be replaced with underscore (_).
"""

TAXON = """Taxonomy ID: {}
Scientific name: {}
Common name: {}
Rank: {}
Lineage: {}
"""


def main():
    des = "Searching taxonomy information from NCBI Taxonomy Database."
    
    epilog = """
Without specifying an email address via '-e' flag, the command-line tool will
create a local SQLite database using data retrieved from NCBI Taxonomy database.
Using this mode, a SQLite database file named '.NCBITaxonomy.sqlite' will be
saved to user's home directory. During the local database initial stage, the
version of the local database will be compared with NCBI Taxonomy database, if
a new version was found, the local database will be updated automatically.

In case you do not want to save a local SQLite database file, you can pass your
email address via '-e' flag to use Entrez Programming Utilities. However, at
the current stage, this mode requires Bio.Entrez module inside Biopython.
    """
    
    formatter = argparse.RawTextHelpFormatter
    parse = argparse.ArgumentParser(description=des,
                                    prog='taxonomy',
                                    usage='%(prog)s ITEM [OPTIONS]',
                                    epilog=epilog,
                                    formatter_class=formatter)

    parse.add_argument('ITEM',
                       help=ITEM_HELP)
    parse.add_argument('-l', '--lineage', action='store_true',
                       help='Search and output lineage information.')
    parse.add_argument('-e', '--email',
                       help='E-mail address for searching NCBI taxonomy using\n'
                            'Entrez Programming Utilities without creating a\n'
                            'local taxonomy database.')
    parse.add_argument('-v', '--verbose', action='store_true',
                       help='Invoke verbose mode for searching taxonomy data.')
    
    args = parse.parse_args()
    item, email, verbose = args.ITEM, args.email, args.verbose
    lineages = args.lineage
    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)

    items = item.replace('_', ' ').split(',') if ',' in item else [item]
    n = len(items)
    if n == 1:
        info('Searching one item in NCBI Taxonomy database.')
    else:
        info('Searching {} items in NCBI Taxonomy database.'.format(n))

    if email:
        info('Initializing Entrez Programming Utilities ... ')
        taxa = entrez.search(items, email)
    else:
        info('Initializing local NCBI Taxonomy Database ... ')
        taxa = database.search(items, lineages)
        
    if taxa:
        info('Done. Found records for {} searching items.'.format(len(taxa)))
        print('')
        for taxon in taxa:
            headers = ['Taxonomy ID', 'Scientific name', 'Common name',
                       'Rank', 'Lineage']
            for i, header in enumerate(headers):
                if i == 4:
                    if lineages:
                        lineage = '; '.join(['{ScientificName}({TaxId})'
                                            .format(**l)
                                             for l in taxon[i]])
                        print('Lineage: {}'.format(lineage))
                else:
                    print('{}: {}'.format(header, taxon[i]))
            print('')
    else:
        info('Done. Not found any results for searching items.')


if __name__ == '__main__':
    main()
