#! /usr/bin/env python

"""
Tests the generated zoneinfo module.

"""

from datetime import datetime, timedelta
import unittest

import zoneinfo

class TestZoneinfo(unittest.TestCase):
    def test_general_functionality(self):
        """
        Make sure the basic functions (through datetime) don't throw exceptions
        for all of the timzeones.

        """
        for _, tz in zoneinfo.timezones.items():
            now = datetime.now(tz)
            now.utcoffset()
            now.dst()
            now.strftime("%H:%M:%S %Z")

    def test_mst_mdt(self):
        mst = zoneinfo.timezones['US/Mountain']
        pst = zoneinfo.timezones['US/Pacific']
        dt = datetime(2011, 7, 4, 0, 0, tzinfo=mst)
        self.assertEqual(dt.utcoffset(), timedelta(hours=-8))
        self.assert_("MDT" in dt.strftime("%Y %M %D %h:%m %Z"), "'MDT' not in %r" % (dt.strftime("%Y %M %D %h:%m %Z"),))

        dtp = dt.astimezone(pst)
        adjusted_mt = dt - timedelta(hours=1)
        self.assertEqual(adjusted_mt.timetuple(), dtp.timetuple())

        dt = datetime(2011, 1, 4, 0, 0, tzinfo=mst)
        self.assertEqual(dt.utcoffset(), timedelta(hours=-7))
        self.assert_("MST" in dt.strftime("%Y %M %D %h:%m %Z"), "'MST' not in %r" % (dt.strftime("%Y %M %D %h:%m %Z"),))


if __name__ == "__main__":
    unittest.main()

