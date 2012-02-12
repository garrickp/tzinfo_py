#! /usr/bin/env python

"""
Script which actually drives the compilation of the zoneinfo data into the
zoneinfo package.

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

import argparse
import os
import sys

import parse
import rulecompile
import linkcompile
import zonecompile
import render

zoneinfo_files = ["africa",
                  "antartica",
                  "asia",
                  "australasia",
                  "backward",
                  "etcetera",
                  "europe",
                  "factory",
                  "northamerica",
                  "pacificnew",
                  "solar87",
                  "solar88",
                  "solar89",
                  "southamerica",
                  "systemv",
                 ]
na_file = "/home/garrickp/Downloads/tzdata2011n/northamerica" # XXX

def main(zoneinfo_data_path):
    if not os.path.exists(zoneinfo_data_path):
        sys.stderr.write("Path does not exist\n")
        sys.exit(1)

    zones = {}
    rules = {}
    links = {}
    for file_path in [os.path.join(zoneinfo_data_path, x) for x in zoneinfo_files]:
        zones, rules, links = parse.parse(file_path, zones, rules, links)
        rulesets = rulecompile.compile(rules)
        zonesets = zonecompile.compile(zones)
        linksets = linkcompile.compile(links)

    render.write_zonefile("northamerica", rulesets, zonesets, linksets)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("path", nargs=1,
                        help="path to the zoneinfo data files")

    args = parser.parse_args()

    main(args.path[0])

