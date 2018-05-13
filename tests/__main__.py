#!/usr/bin/env python3

import sys
import os
import unittest

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.split(ROOT_DIR)[0]
sys.path.append(ROOT_DIR + "/dht_crawler")

LOADER = unittest.TestLoader()
TESTSUITE = LOADER.discover('unit')
TESTRUNNER = unittest.TextTestRunner(verbosity=2)
TESTRUNNER.run(TESTSUITE)
