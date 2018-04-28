#!/usr/bin/env python3
'''
Setup script to install dht-crawler
'''
from distutils.core import setup

setup(name='dht_crawler',
      version='1.0',
      description='Simple dht crawler with different experimental mechanics.',
      url='https://github.com/Matovidlo/DHT-crawler',
      author='Martin Vaško',
      author_email='matovidlo2@gmail.com',
      packages=['dht_crawler'],
      requires=['bencoder', 'bencode'],
      # py_modules=['bencoder'],
      classifiers=[
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      long_description=open('README.md').read(),
     )
