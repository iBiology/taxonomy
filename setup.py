#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

VERSION = '1.0'

wd = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(wd, 'README.md')) as f:
        return f.read()


setup(name='taxonomy',
      version=VERSION,
      description="""A command-line tool for searching taxonomy information
      from NCBI Taxonomy Database.""",
      long_description=readme(),
      url='https://github.com/iBiology/taxonomy',
      author='FEI YUAN',
      author_email='yuanfeifuzzy@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['venv']),
      entry_points={
          'console_scripts': ['taxonomy=taxonomy.taxonomy:main']
          },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          ],
      keywords='taxonomy SQLite Entrez Biology Bioinformatics'
      )


if __name__ == '__main__':
    pass
