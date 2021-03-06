"""
Parser module, which parses the zoneinfo files & returns corresponding python
objects that can be transformed into tzinfo objects.

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

from datetime import datetime
import re

LAST_ZONE_SENT = '__last_processed_zone__'
zone_re = re.compile(r'\A(Zone)\s([a-zA-Z0-9/_+-]+)\s+(-?\d{1,2}:?\d{0,2}:?\d{0,2})\s(-|[a-zA-Z0-9/_+\-]+)\s+(".*"|[\w+%-]+)\s?(\d{4} ?\w{0,3} *\d{0,2} *\d{0,2}:?\d{0,2}:?\d{0,2}[us]?)?$')
			#-5:00	US	E%sT	1920
zone_cont_re = re.compile(r'\A\s*(-?\d{1,2}:?\d{0,2}:?\d{0,2})\s*(\d:\d\d|-|[a-zA-Z0-9/_+\-]+)?\s(".*"|[\w+%/-]+)\s?(\d{4} ?\w{0,3} *[0-9a-zA-Z>=]* *\d{0,2}:?\d{0,2}:?\d{0,2}[us]?)?$')
link_re = re.compile(r'\A(Link)\s([a-zA-Z0-9/_+\-]+)\s+([a-zA-Z0-9/_+\-]+)$')
rule_re = re.compile(r'\A(Rule)\s([\w-]+)\s(\d+|min)\s(\d{4}|max|only)\s(.+)\s(\w+)\s(.+)\s([\w:-]+)\s([\w:-]+)\s([\w-]+)$')

class ParseError(Exception):
    pass

def parse_rule(line, rules):
    match = rule_re.match(line)

    if not match:
        raise ParseError("Unable to parse rule: %r" % (line,))

    parts = match.groups()

    if parts[0] != "Rule":
        raise ParseError("parse mismatch, expecting 'Rule', got %r" % (parts[0],))

    try:
        this_rule = {
                     "name":    parts[1],
                     "from":    parts[2],
                     "to":      parts[3],
                     "type":    parts[4],
                     "in":      parts[5],
                     "on":      parts[6],
                     "at":      parts[7],
                     "save":    parts[8],
                     "letter":  parts[9],
                    }

    except IndexError:
        raise ParseError("not enough elements in this line to parse a rule: %r" % (line,))

    name = this_rule['name']

    try:
        rules[name].append(this_rule)

    except KeyError:
        rules[name] = [this_rule]

def parse_zone(line, zones):

    if not line.startswith("Zone"):
        match = zone_cont_re.match(line)

        if not match:
            raise ParseError("Unable to parse continuation line: %r" % (line,))

        parts = match.groups()
        offset = {
                  "gmtoff": parts[0],
                  "rules": parts[1],
                  "format": parts[2],
                  "until": parts[3],
                 }

        this_zone = zones[LAST_ZONE_SENT]
        this_zone['offsets'].append(offset)

    else:
        match = zone_re.match(line)

        if not match:
            raise ParseError("Unable to parse zone line: %r" % (line,))

        parts = match.groups()
        this_zone = {
                     "name": parts[1],
                     "offsets": [
                                 {"gmtoff": parts[2],
                                  "rules": parts[3],
                                  "format": parts[4],
                                  "until": parts[5],
                                 },
                                ],
                    }

    name = this_zone['name']

    zones[LAST_ZONE_SENT] = this_zone

    zones[name] = this_zone


def parse_link(line, links):
    match = link_re.match(line)

    if not match:
        raise ParseError("Unable to parse link line: %r" % (line,))

    parts = match.groups()

    if parts[0] != "Link":
        raise ParseError("parse mismatch, expecting 'Link', got %r" % (parts[0],))

    try:
        this_link = {
                     "to":    parts[1],
                     "from":      parts[2],
                    }

    except IndexError:
        raise ParseError("not enough elements in this line to parse a link: %r" % (line,))

    name = this_link['from']

    links[name] = this_link

def parse(f_path, zones={}, rules={}, links={}):

    try:
        with open(f_path, 'r') as zi_file:
            last = None
            for line in zi_file:

                if '#' in line:
                    line = line[:line.find('#')]

                line = line.strip()

                if not line:
                    continue

                if line.startswith("Rule"):
                    parse_rule(line, rules)
                    last = "Rule"

                elif line.startswith("Zone"):
                    parse_zone(line, zones)
                    last = "Zone"

                elif line.startswith("Link"):
                    parse_link(line, links)
                    last = "Link"

                elif last == "Zone":
                    parse_zone(line, zones)
                    last="Zone"

                else:
                    raise ParseError("I don't know how to parse %r" % (line,))

    except IOError:
        pass

    if LAST_ZONE_SENT in zones:
        del(zones[LAST_ZONE_SENT])

    return (zones, rules, links)
