"""
Compile link data into linksets.

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

INDENT = '    '

class CompileError(Exception):
    pass

def name_to_identifier(name):
    return name.replace('/', '_').replace('-', '_').replace('+', 'plus')

class ASO(object):
    pass
class Link(ASO):
    def __init__(self, n):
        self.name = n
        self.code_name = None
        self.linkfrom_code_name = None
        self.linkto_code_name = None

    def render(self, level=0):
        yield('\n')
        yield(INDENT * level)
        for x in self.linkfromcode_name.render(level):
            yield(x)
        yield(' = ')
        for x in self.linkto_code_name.render(level):
            yield(x)

class Identifier(ASO):
    def __init__(self, n):
        self.name = n

    def render(self, level=0):
        yield(self.name)

def compile(links):
    all_links = {}
    for _, link in links.items():

        link_o = Link(link['from'])
        link_o.code_name = name_to_identifier(link['from'])
        link_o.linkfromcode_name = Identifier(name_to_identifier(link['from']))
        link_o.linkto_code_name = Identifier(name_to_identifier(link['to']))

        all_links[link['from']] = link_o
    return all_links
