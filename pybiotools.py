#! /usr/bin/env python
from argparse import ArgumentParser

from os import path
import sys
import traceback
from sys import argv

from lib.scripts.biotoolscript import BiotoolScript
from lib.scripts.base_script import BaseScript


class PyBiotools(BiotoolScript):
    def __init__(self, args, root):
        super(PyBiotools, self).__init__(args, root, "PyBiotools scripts interface")

    def _build_parser(self, parser):
        parser.add_argument("script", help="Define the program to be executed")
        return parser

    def run(self):
        script = None
        for s in self.__scripts():
            if s.__name__ == self._get_option('script'):
                script = s
                break

        if script is None:
            self.__unknown_script()
        else:
            script = script(argv[2:], self._root())
            script.run()

    def __unknown_script(self):
        ignore = (PyBiotools, BaseScript, BiotoolScript)
        str = ""
        for script in self.__scripts():
            if not ignore.__contains__(script) :
                str += "\t{:<24} - {:5}\n".format(script.__name__,
                                               script.description())

        self._parser().error("\nYou must choose one script to run from the "
                             "following:\n%s" % str)

    def __scripts(self):
        scripts = set()
        work = [BiotoolScript]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in scripts:
                    scripts.add(child)
                    work.append(child)
        return sorted(scripts, key=(lambda x: x.__name__))

    def _report(self):
        print "Endend Main"

if __name__ == "__main__":
    try:
        script = PyBiotools(argv[1:2], path.dirname(path.abspath(__file__)))
        script.run()
    except KeyboardInterrupt:
        print "Keyboar Interrupt main..."
