"""
Compile zone data into zone classes.

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

import re

# # Zone  NAME        GMTOFF  RULES   FORMAT  [UNTIL]
# Zone America/Detroit    -5:32:11 -  LMT 1905
#             -6:00   -   CST 1915 May 15 2:00
#             -5:00   -   EST 1942
#             -5:00   US  E%sT    1946
#             -5:00   Detroit E%sT    1973
#             -5:00   US  E%sT    1975
#             -5:00   -   EST 1975 Apr 27 2:00
#             -5:00   US  E%sT

# Target code should look something like this (minus comments and whitespace):

# class America_Detroit(tzinfo):
#     def __from_rules(self, dt):
#         offset = None
#         rule = None
#         save = None
#         format = None
#         letter = None
#
#         # Here's the meat and bones of the generated content
#         if dt.year <= 1905:
#             offset = timedelta(hours=-5, minutes=-32, seconds=-11)
#             format = "LMT"
#             rule = None
#         elif dt <= datetime(1915, 5, 15, 2, 0):
#             offset = timedelta(hours=-6)
#             format = "CST"
#             rule = None
#         elif dt.year <= 1946:
#             offset = timedelta(hours=-5)
#             format = "E%sT"
#             rule = __us
#         else:
#             offset = timedelta(hours=-5)
#             format = "E%sT"
#             rule = __us
#
#         # The following is pretty much constant
#         if rule is not None:
#             save, letter = rule()
#         if offset is not None and save is not None:
#             offset = offset - save
#         if format is not None and letter is not None:
#             format = format % letter
#         return offset, save, format
# 
#     def utcoffset(self, dt):
#         offset, _, _ = self.__from_rules(dt)
#         return offset.total_seconds // 60
#     def dst(self, dt):
#         _, save, _ = self.__from_rules(dt)
#         return 0 - (save.total_seconds // 60)
#     def tzname(self, dt):
#         _, _, format = self.__from_rules(dt)
#         return format

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
INDENT = '    '

def name_to_identifier(name):
    return name.replace('/', '_').replace('-', '_').replace('+', 'plus')

class CompileError(Exception):
    pass

class ASO(object):
    pass

class Zone(ASO):
    def __init__(self, n):
        self.name = n
        self.code_name = name_to_identifier(n)
        self.offsets = []

    def render(self, level=0):
        yield('\n')
        yield(INDENT * level)
        yield('class ')
        yield(self.code_name)
        yield('(tzinfo):')
        level += 1
        yield('\n')
        yield(INDENT * level)
        yield('def __from_rules(self, dt):')
        level += 1
        for x in ('rule','format','letter'):
            yield('\n')
            yield(INDENT * level)
            yield(x)
            yield(' = None')
        for x in ('offset', 'save'):
            yield('\n')
            yield(INDENT * level)
            yield(x)
            yield(' = timedelta()')
        yield('\n')
        yield(INDENT * level)
        yield('dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)')
        first = True
        for o in self.offsets:
            for x in o.render(level, first):
                yield(x)
            first = False
        for line in ["if rule is not None:",
                     "    save, letter = rule(dt)",
                     "if offset is not None and save is not None:",
                     "    offset = offset - save",
                     "if format is not None and letter is not None and '%' in format:",
                     "    format = format % letter",
                     "return offset, save, format"]:
            yield('\n')
            yield(INDENT * level)
            yield(line)
        level -= 1
        for line in ["def utcoffset(self, dt):",
                     "    offset, _, _ = self.__from_rules(dt)",
                     "    return offset",
                     "def dst(self, dt):",
                     "    _, save, _ = self.__from_rules(dt)",
                     "    return save",
                     "def tzname(self, dt):",
                     "    _, _, format = self.__from_rules(dt)",
                     "    return format"]:
            yield('\n')
            yield(INDENT * level)
            yield(line)

class Offset(ASO):
    def __init__(self):
        self.condition = None
        self.assignments = []

    def render(self, level=0, first=False):
        if self.condition:
            yield('\n')
            yield(INDENT * level)
            if first:
                yield('if ')
            else:
                yield('elif')
            for x in self.condition.render(level):
                yield(x)
            yield(':')
            level += 1
        else:
            if not first:
                yield('\n')
                yield(INDENT * level)
                yield('else:')
                level += 1
        for a in self.assignments:
            for x in a.render(level):
                yield(x)

class Assignment(ASO):
    def __init__(self, n, v):
        self.name = n
        self.value = v

    def render(self, level=0):
        yield('\n')
        yield(INDENT * level)
        yield(self.name)
        yield(' = ')
        if isinstance(self.value, ASO):
            for x in self.value.render(level):
                yield(x)
        else:
            yield(repr(self.value))

class Condition(ASO):
    def __init__(self, n, o, v):
        self.name = n
        self.operator = o
        self.value = v

    def render(self, level=0):
        yield('(')
        yield(self.name)
        yield(' %s ' % (self.operator,))
        if isinstance(self.value, ASO):
            for x in self.value.render(level):
                yield(x)
        else:
            yield(repr(self.value))
        yield(')')

class FuncCall(ASO):
    def __init__(self, n, *args, **kwargs):
        self.name = n
        self.args = args
        self.kwargs = kwargs

    def render(self, level=0):
        yield(self.name)
        yield('(')
        first = True
        for a in self.args:
            if not first:
                yield ", "
            else:
                first = False
            if isinstance(a, ASO):
                for x in a.render(level):
                    yield(x)
            else:
                yield(repr(a))

        for k, v in self.kwargs.items():
            if not first:
                yield ", "
            else:
                first = False
            yield(k)
            yield('=')
            if isinstance(v, ASO):
                for x in v.render(level):
                    yield(x)
            else:
                yield(repr(v))
        yield(')')

class Identifier(ASO):
    def __init__(self, n):
        self.name = n

    def render(self, level=0):
        yield(self.name)

def compile(zones):
    all_zones = {}
    for name, zone in zones.items():
        offsets = zone['offsets']

        z_obj = Zone(name)

        for offset in offsets:

            # Get and set up gmt offset
            o_obj = Offset()

            try:
                gmt_off = re.match(r'( ?-?)?(\d+):?(\d+)?:?(\d+)?', offset['gmtoff']).groups()
            except AttributeError:
                raise CompileError("Error parsing gmtoff: %r" % (offset['gmtoff'],))

            neg = gmt_off[0] == '-'
            hours = int(gmt_off[1])
            mins = int(gmt_off[2]) if gmt_off[2] else 0
            secs = int(gmt_off[3]) if gmt_off[3] else 0

            if neg:
                hours = -hours
                mins = -mins
                secs = -secs

            o_obj.assignments.append(Assignment('offset', FuncCall('timedelta',
                                     hours=hours, minutes=mins, seconds=secs)))

            # Get and set up rule assignment
            rule = offset['rules']
            if not rule or rule.strip() == '-':
                rule_name = None
            elif re.match(r'\d{1,2}:?\d{0,2}:?\d{0,2}', rule):
                rule_name = {'1:00': '_rule_constant_1hour',
                             '0:30': '_rule_constant_30min',
                             '0:20': '_rule_constant_20min'}[rule.strip()]
            else:
                rule_name = '_' + name_to_identifier(rule)

            o_obj.assignments.append(Assignment('rule', Identifier(rule_name)))

            # Get and set up format
            fmt = offset['format']

            o_obj.assignments.append(Assignment('format', fmt))

            # Get and set up the condition
            if offset['until']:
                # TODO These times appear to be local in the file, which could
                #      wreak all sorts of havok with conversions. Fix this!
                try:
                    u_parts = re.match(r'(\d{4}) ?(\w{3})? ?(\d+)? ?(\d+)?:?(\d+)?',
                                       offset['until']).groups()
                except AttributeError:
                    raise CompileError("Error parsing until: %r" % (offset['until'],))

                u_year = int(u_parts[0])
                u_mon = u_parts[1]
                u_day = int(u_parts[2]) if u_parts[2] else 1
                u_hour = int(u_parts[3]) if u_parts[3] else 0
                u_mins = int(u_parts[4]) if u_parts[4] else 0

                try:
                    u_mon_i = MONTHS.index(u_mon) + 1 if u_mon else 1
                except ValueError:
                    raise CompileError("Not able to index month %r" % (rule['in'],))

                comp = Condition('dt', '<', Identifier('datetime(%s,%s,%s,%s,%s)' % (u_year, u_mon_i, u_day, u_hour, u_mins)))

                o_obj.condition = comp
            z_obj.offsets.append(o_obj)
        all_zones[name] = z_obj
    return all_zones
