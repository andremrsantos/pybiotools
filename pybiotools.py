#! /usr/bin/env python

from os import path
from optparse import OptionParser
import sys
import traceback
from lib.biotoolscript import BiotoolScript
from sys import argv
import lib.scripts


class DefaultScript(BiotoolScript):
    def _build_parser(self):
        parser = OptionParser("Usage: %prog [program] [options]")
        return parser

    def _build(self):
        if not self._has_arg(0):
            self.__unknown_script()

    @staticmethod
    def description():
        return "Default script for redirecting call for others scripts"

    def run(self):
        scripts = BiotoolScript.__subclasses__()
        script = None
        for i in scripts:
            if i.__name__ == self._get_arg(0):
                script = i
        if script is None:
            self.__unknown_script()
        else:
            inst = script(argv[2:], self._root())
            inst.run()

    def __unknown_script(self):
        str = ""
        for script in BiotoolScript.__subclasses__():
            if script != DefaultScript:
                str += "%20s - %s\n" % (script.__name__,
                                        script.description())

        self._parser().error("You must choose one script to run from the "
                             "following:\n%s" % str)


def main():
    script = DefaultScript(argv[1:2], path.dirname(path.abspath(__file__)))
    try:
        script.run()
        return 0
    except Exception as e:
        traceback.print_exc(sys.stderr)
        sys.stderr.write("%s : %s\n" % (e.__class__.__name__, e.message))
        sys.stderr.flush()
        return 1

if __name__ == "__main__":
    main()