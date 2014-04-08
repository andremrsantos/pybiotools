#! /usr/bin/env python
import sys
from lib.biotoolscript import BiotoolScript

__author__ = 'andresantos'

class BaseScript(BiotoolScript):
    def _build_parser(self, parser):
        parser.add_option('-i', '--input', dest='input',
                          help='Input file used to perform analysis')
        parser.add_option('-o', '--output', dest='output',
                          help='Output file destination', default = sys.stdout)
        return parser

    def _build(self):
        out = self._get_option('output')
        sys.stdout = out