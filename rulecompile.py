"""
Compile rule data into rulesets.

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

# Sample rule data with header
# # Rule  NAME    FROM    TO  TYPE    IN  ON  AT  SAVE    LETTER/S
# Rule    US  1918    1919    -   Mar lastSun 2:00    1:00    D
# Rule    US  1918    1919    -   Oct lastSun 2:00    0   S
# Rule    US  1942    only    -   Feb 9   2:00    1:00    W # War
# Rule    US  1945    only    -   Aug 14  23:00u  1:00    P # Peace
# Rule    US  1945    only    -   Sep 30  2:00    0   S
# Rule    US  1967    2006    -   Oct lastSun 2:00    0   S
# Rule    US  1967    1973    -   Apr lastSun 2:00    1:00    D
# Rule    US  1974    only    -   Jan 6   2:00    1:00    D
# Rule    US  1975    only    -   Feb 23  2:00    1:00    D
# Rule    US  1976    1986    -   Apr lastSun 2:00    1:00    D
# Rule    US  1987    2006    -   Apr Sun>=1  2:00    1:00    D
# Rule    US  2007    max -   Mar Sun>=8  2:00    1:00    D
# Rule    US  2007    max -   Nov Sun>=1  2:00    0   S

# Target code should look something like this (minus comments & whitespace):
# def __rule_us(dt):
#     s = 0
#     l = ''
# 
#     # Rule    US  1918    1919    -   Mar lastSun 2:00    1:00    D
#     if dt.year >= 1918 and dt.year <= 1919 and dt >= __lastSun(dt.year, 3, 2, 0):
#         s = timedelta(hours=1)
#         l = 'D'
# 
#     # Rule    US  1942    only    -   Feb 9   2:00    1:00    W # War
#     if dt.year == 1942 and dt >= datetime(dt.year, 2, 9, 2, 0)
#         s = timedelta(hours=1)
#         l = 'W'
# 
#     # Rule    US  2007    max -   Mar Sun>=8  2:00    1:00    D
#     if dt.year >= 2007 and dt >= __sunGtEq(dt.year, 3, 8, 2, 0)
#         s = timedelta(hours=1)
#         l = 'D'

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
INDENT = '    '

# TODO Clean up to attempt to match PEP8

class CompileError(Exception):
    pass

# TODO Get this into some kind of common module - too much code duplication
class ASO(object):
    pass
class RuleSet(ASO):
    def __init__(self, n):
        self.name = n
        self.initial_assignments = [Assignment('s', None), Assignment('l', None)]
        self.rule_elements = []

    def render(self, level=0):
        yield('\n')
        yield(INDENT * level)
        yield('def __')
        yield(self.name)
        yield('(dt):')
        for a in self.initial_assignments:
            for x in a.render(level + 1):
                yield(x)
        for r_ele in self.rule_elements:
            for x in r_ele.render(level + 1):
                yield(x)
        yield('\n')
        yield(INDENT * (level + 1))
        yield('return (s, l)')

class RuleElement(ASO):
    def __init__(self):
        self.conditions = []
        self.assignments = []

    def render(self, level=0):
        yield('\n')
        yield(INDENT * level)
        yield('if ')
        first=True
        for c in self.conditions:
            if not first:
                yield(' and ')
            else:
                first = False
            for x in c.render(level + 1):
                yield x
        if first:
            yield('True')
        yield(':')
        for a in self.assignments:
            for x in a.render(level + 1):
                yield x

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

def compile(rules):
    all_rulesets = {}
    for _, rule_list in rules.items():
        for rule in rule_list:
            # TODO Get logic for all the re.match and ints out of here and
            #      into parse
            r_ele = RuleElement()
            try:
                # Fix for systemV rule entry
                if rule['from'] == 'min':
                    from_yr = 0
                else:
                    from_yr = int(rule['from'])

                if rule['to'] == 'only':
                    r_ele.conditions.append(Condition('dt.year', '==', from_yr))
                elif rule['to'] == 'max':
                    r_ele.conditions.append(Condition('dt.year', '>=', from_yr))
                else:
                    r_ele.conditions.append(Condition('dt.year', '>=', from_yr))
                    r_ele.conditions.append(Condition('dt.year', '<=', int(rule['to'])))
            except ValueError:
                raise CompileError("Problem creating condition for 'from %r to %r'"
                                   % (rule['from'], rule['to']))

            try:
                in_mo = MONTHS.index(rule['in']) + 1
            except ValueError:
                raise CompileError("Not able to index month %r" % (rule['in'],))

            try:
                on_day = int(rule['on'])
            except ValueError:
                on_day = None

            try:
                at_h_m = re.match(r'(\d+):?(\d+)?', rule['at']).groups()
                at_hour = int(at_h_m[0])
                at_min = int(at_h_m[1]) if at_h_m[1] else 0
            except AttributeError:
                raise CompileError("unable to turn %r to hours:minutes" % (rule['at'],))

            if on_day:
                f_call = FuncCall('datetime', Identifier('dt.year'), in_mo, on_day, int(at_hour), int(at_min))
            else:
                if any([x in rule['on'] for x in ('=','>','<')]):
                    try:
                        f_name, d = re.match(r'( ?[a-zA-Z<>=]+)(\d+)', rule['on']).groups()
                        d = int(d)
                    except Exception:
                        raise CompileError("Problem extracting day from %r" % (rule['on'],))
                    f_name = f_name.replace('>', 'Gt')
                    f_name = f_name.replace('<', 'Lt')
                    f_name = f_name.replace('=', 'Eq')
                    f_call = FuncCall('__' + f_name, Identifier('dt.year'), in_mo, d, int(at_hour), int(at_min))
                else:
                    f_call = FuncCall('__' + rule['on'], Identifier('dt.year'), in_mo, int(at_hour), int(at_min))
            r_ele.conditions.append(Condition('dt', '>=', f_call))

            r_ele.assignments.append(Assignment('l', "%s" % (rule['letter'],)))
            try:
                off_h_m_s = re.match(r'(-)?(\d+):?(\d+)?:?(\d+)?', rule['save']).groups()
                neg = bool(off_h_m_s[0])
                h = int(off_h_m_s[1])
                m = int(off_h_m_s[2]) if off_h_m_s[2] else 0
                s = int(off_h_m_s[3]) if off_h_m_s[3] else 0
            except AttributeError:
                raise CompileError("unable to convert save: %r" % (rule['save'],))
            if neg:
                h = -h
                m = -m
                s = -s
            r_ele.assignments.append(Assignment('s', FuncCall('timedelta', hours=h, minutes=m, seconds=s)))

            if rule['name'] in all_rulesets:
                r_set = all_rulesets[rule['name']]
            else:
                r_set = RuleSet(rule['name'])

            r_set.rule_elements.append(r_ele)
            all_rulesets[rule['name']] = r_set

    return all_rulesets

