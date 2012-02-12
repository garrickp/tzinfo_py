#! /usr/bin/env python

"""
Tests the generated zoneinfo module.

"""

from datetime import datetime
import unittest

import zoneinfo

class TestZoneinfo(unittest.TestCase):
    def test_general_functionality(self):
        for _, tz in zoneinfo.timezones.items():
            now = datetime.now(tz)
            now.utcoffset()
            now.dst()
            now.strftime("%H:%M:%S %Z")

if __name__ == "__main__":
    unittest.main()

