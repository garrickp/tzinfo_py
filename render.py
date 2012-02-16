"""
Module to render the view (the zoneinfo package) from the models.

Copyright (c) 2012 Garrick Peterson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import os
import datetime

license = """
Copyright (c) %d Garrick Peterson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

""" % (datetime.datetime.now().year,)
PKG_NAME = 'zoneinfo'
GENERATOR_URL = "https://github.com/garrickp/tzinfo_py"

HELPER_FUNCS = """
# Support functions for rules that rely on calendar days
def __lastSun(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[6]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastSat(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[5]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastFri(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[4]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastThu(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[3]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastWed(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[2]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastTue(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[1]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __lastMon(year, month, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in reversed(c):
        day = w[0]
        if day != 0:
            break
    return datetime(year, month, day, hour, min)
def __SunGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[6]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __SatGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[5]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __FriGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[4]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __ThuGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[3]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __WedGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[2]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __TueGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[1]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)
def __MonGtEq(year, month, min_day, hour, min):
    c = Calendar().monthdayscalendar(year, month)
    day = 0
    for w in c:
        day = w[0]
        if day >= min_day:
            break
    return datetime(year, month, day, hour, min)

# Constant rules
def _rule_constant_1hour(dt):
    return (timedelta(hours=1), '')
def _rule_constant_30min(dt):
    return (timedelta(minutes=30), '')
def _rule_constant_20min(dt):
    return (timedelta(minutes=20), '')

"""

def write_zonefile(name, rulesets, zonesets, linksets):
    with open("zoneinfo.py", 'w') as outf:
        outf.write('"""\n')
        outf.write("generated %s file\n\n" % (PKG_NAME,))
        outf.write("Generated from: %s\n" % (GENERATOR_URL,))
        outf.write(license)
        outf.write('"""\n\n')
        outf.write('from datetime import tzinfo, datetime, timedelta\n')
        outf.write('from calendar import Calendar\n')
        outf.write(HELPER_FUNCS)

        outf.write("# Rule sets")
        for _, r in rulesets.items():
            outf.writelines((str(x) for x in r.render()))
        outf.write("\n# Zones sets")
        for _, z in zonesets.items():
            outf.writelines((str(x) for x in z.render()))
        outf.write("\n# Links")
        for _, l in linksets.items():
            outf.writelines((str(x) for x in l.render()))

        outf.write("\n\ntimezones = {\n")
        for _, z in zonesets.items():
            outf.write('    ' * 2)
            outf.write('"%s": %s(),\n' % (z.name, z.code_name))
        for _, l in linksets.items():
            outf.write('    ' * 2)
            outf.write('"%s": %s(),\n' % (l.name, l.code_name))
        outf.write("}\n")
