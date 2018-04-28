#!/usr/bin/env python3

import sys
import unittest

sys.path.append('../dht_crawler')

LOADER = unittest.TestLoader()
TESTSUITE = LOADER.discover('unit')
TESTRUNNER = unittest.TextTestRunner(verbosity=2)
TESTRUNNER.run(TESTSUITE)
