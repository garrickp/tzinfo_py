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

def write_zonefile(name, rulesets, zonesets, linksets):
    with open("zoneinfo.py", 'w') as outf:
        outf.write('"""\n')
        outf.write("generated %s %s file\n" % (name, PKG_NAME))
        outf.write(license)
        outf.write('"""\n\n')
        outf.write('from datetime import tzinfo, datetime, timedelta\n\n')

        for _, r in rulesets.items():
            outf.writelines((str(x) for x in r.render()))
        for _, z in zonesets.items():
            outf.writelines((str(x) for x in z.render()))
        for _, l in linksets.items():
            outf.writelines((str(x) for x in l.render()))

        outf.write("\ntimezones = {\n")
        for _, z in zonesets.items():
            outf.write('    ' * 2)
            outf.write('"%s": %s,\n' % (z.name, z.code_name))
        for _, l in linksets.items():
            outf.write('    ' * 2)
            outf.write('"%s": %s,\n' % (l.name, l.code_name))
        outf.write("}\n")
