#!/usr/bin/env python3

import sys
import os
import re
import unittest

sys.path.append('./dht_crawler')
sys.path.append('../dht_crawler')

LOADER = unittest.TestLoader()
CWD = os.getcwd()
CWD = re.search(r"([^\/]+)$", CWD)
CWD = CWD.group(0)
if CWD == "tests":
    TESTSUITE = LOADER.discover('unit')
elif CWD == "monitoring" or CWD == "DHT-crawler":
    TESTSUITE = LOADER.discover('tests')

TESTRUNNER = unittest.TextTestRunner(verbosity=2)
TESTRUNNER.run(TESTSUITE)
