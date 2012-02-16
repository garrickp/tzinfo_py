#! /usr/bin/env python

"""
Tests the generated zoneinfo module.

"""

from datetime import datetime, timedelta, time
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

    def test_time(self):
        mst = zoneinfo.timezones['US/Mountain']
        t = time(20, 35, tzinfo=mst)

        self.assert_('-07:00' in t.isoformat() or '-08:00' in t.isoformat())

    def test_historical_sample(self):
        ab = zoneinfo.timezones['Asia/Baku']
        dt = datetime(1991, 8, 30, 12, 0, tzinfo=ab)
        self.assertEqual(dt.utcoffset(), timedelta(hours=2))

        vi = zoneinfo.timezones['America/Indiana/Vincennes']
        dt = datetime(1955, 6, 1, 12, 0, tzinfo=vi)
        self.assertEqual(dt.utcoffset(), timedelta(hours=-7))

        ad = zoneinfo.timezones['Australia/Darwin']
        dt = datetime(1872, 1, 1, 12, 0, tzinfo=ad)
        self.assertEqual(dt.utcoffset(), timedelta(hours=8, minutes=43))

if __name__ == "__main__":
    unittest.main()

