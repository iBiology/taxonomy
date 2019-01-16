# *taxonomy*

A command-line tool for searching taxonomy information from NCBI Taxonomy 
Database.

## Features
* Searching taxonomy information via a local SQLite Database.
* Searching taxonomy information via Entrez Programming Utilities (Bio.Entrez).

## Install *taxonomy*
*taxonomy* runs on Python 2.7 and Python 3.3 or above, if you are already
familiar with installation of Python packages, you can easily install *taxonomy*
from PyPI with the following command on all major platforms (Windows, MacOS, 
or Linux):

```bash
$ pip install taxonomy
```

It is strongly recommended that you install *taxonomy* in a dedicated 
virtualenv, to avoid conflicting with your system packages.


### Install *taxonomy* to a virtual environment (recommended)

I recommend installing *taxonomy* inside a virtual environment on all platforms.

Python packages can be installed either globally (a.k.a system wide), or in
a user specified space. We not recommend you installing *taxonomy* system wide.

Instead, I recommend that you install *taxonomy* within a so-called "virtual
environment" ([virtualenv](https://virtualenv.pypa.io)). Virtualenvs allow 
users 
to not conflict with already-installed Python system packages (which could 
break some of your system tools and scripts), and still install packages 
normally with ``pip`` (without ``sudo`` and the likes).

To get started with virtual environments, see 
[virtualenv installation instructions](https://virtualenv.pypa.io/en/stable/installation/).

## Usage
Once you taxonomy was installed, you can use *taxonomy* in either a Python 
session (not strongly recommended) or from a terminal (recommended). 

For using *taxonomy* in a terminal, check the usage with `-h` first:

```bash
$ taxonomy -h

usage: taxonomy ITEM [OPTIONS]

Searching taxonomy information from NCBI Taxonomy Database.

positional arguments:
  ITEM                  Search item. The item can be a single taxon name
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

optional arguments:

  -e EMAIL, --email EMAIL
                        E-mail address for searching NCBI taxonomy using
                        Entrez Programming Utilities without creating a
                        local taxonomy database.
  -l, --lineage         Search and output lineage information.
  -h, --help            show this help message and exit
  -v, --verbose         Invoke verbose mode for searching taxonomy data.

Without specifying an email address via '-e' flag, the command-line tool will
create a local SQLite database using data retrieved from NCBI Taxonomy database.
Using this mode, a SQLite database file named '.NCBITaxonomy.sqlite' will be
saved to user's home directory. During the local database initial stage, the
version of the local database will be compared with NCBI Taxonomy database, if
a new version was found, the local database will be updated automatically.

In case you do not want to save a local SQLite database file, you can pass your
email address via '-e' flag to use Entrez Programming Utilities. However, at
the current stage, this mode requires Bio.Entrez module inside Biopython.
```

Check taxonomy information through a local database under verbose mode:
```bash
$ taxonomy HUMAN,Sus_scrofa,338296 -v
INFO [taxonomy] Searching 3 items in NCBI Taxonomy database.
INFO [taxonomy] Initializing local NCBI Taxonomy Database ...
INFO [taxonomy] Retrieving data from NCBI Taxonomy to create local database.
INFO [taxonomy] Downloading taxdump (taxdump.tar.gz) from NCBI FTP site (via HTTP).
INFO [taxonomy] Download successfully! Parsing taxdump ...
INFO [taxonomy]     Parsing names (names.dmp) ...
INFO [taxonomy]     Parsing merged ids (merged.dmp) ...
INFO [taxonomy]     Parsing nodes (nodes.dmp) ...
INFO [taxonomy] Creating local database ~/.NCBITaxonomy.sqlite ...
INFO [taxonomy] Creating tables ...
INFO [taxonomy] Uploading data to tables ...
INFO [taxonomy]     Uploading md5 ...
INFO [taxonomy]     Uploading scientific names ...
INFO [taxonomy]     Uploading common names ...
INFO [taxonomy]     Uploading synonym names ...
INFO [taxonomy]     Uploading other names ...
INFO [taxonomy]     Uploading merged taxa IDs ...
INFO [taxonomy]     Uploading nodes ...
INFO [taxonomy] Successfully create local NCBI Taxonomy SQLite Database.
INFO [taxonomy] Local Database was saved to: ~/.NCBITaxonomy.sqlite.
INFO [taxonomy] Searching in local NCBI Taxonomy database
INFO [taxonomy]     Searching taxon ID for taxon HUMAN ...
INFO [taxonomy]     Summarizing search results for taxon HUMAN
INFO [taxonomy]     Searching taxon ID for taxon Sus scrofa ...
INFO [taxonomy]     Summarizing search results for taxon Sus scrofa
INFO [taxonomy]     Searching names for taxon 338296
INFO [taxonomy]     Summarizing search results for taxon 338296
INFO [taxonomy] Done. Found records for 3 searching items.

Taxonomy ID: 9606
Scientific name: Homo sapiens
Common name: human
Rank: species

Taxonomy ID: 9823
Scientific name: Sus scrofa
Common name: pig
Rank: species

Taxonomy ID: 338296
Scientific name: Cosmognathia arcus
Common name:
Rank: species
```

Check taxonomy information through Entrez (using `-e` flag) under verbose mode:
```bash
$ taxonomy HUMAN,Sus_scrofa,338296 -e youremail@address -v
INFO [taxonomy] Searching 3 items in NCBI Taxonomy database.
INFO [taxonomy] Searching 3 items in NCBI Taxonomy database.
INFO [taxonomy] Initializing Entrez Programming Utilities ...
INFO [taxonomy] Searching via Entrez Programming Utilities
INFO [taxonomy] Done. Found records for 3 searching items.

Taxonomy ID: 9606
Scientific name: Homo sapiens
Common name: human
Rank: species

Taxonomy ID: 9823
Scientific name: Sus scrofa
Common name: pig
Rank: species

Taxonomy ID: 338296
Scientific name: Cosmognathia arcus
Common name:
Rank: species
```
