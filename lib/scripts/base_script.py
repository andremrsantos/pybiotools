#! /usr/bin/env python
import sys

from lib.scripts.biotoolscript import BiotoolScript

__author__ = 'andresantos'

class BaseScript(BiotoolScript):
    def _build_parser(self, parser):
        parser.add_argument('-i', '--input', dest='input', required=True,
                            help='Analysis input file')
        parser.add_argument('-o', '--output', dest='output',
                            help='Output file destination')
        return parser

    def _build(self):
	if self._get_option('output') is not None:
            sys.stdout = open(self._get_option('output'), 'w')
