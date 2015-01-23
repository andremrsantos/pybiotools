#! /usr/bin/env python

__author__ = 'Andre M Ribeiro dos Santos'

from sys import argv
from scripts import PyBiotoolsScript


def main():
    script = PyBiotoolsScript()
    script.execute(argv)

if __name__ == '__main__':
    main()