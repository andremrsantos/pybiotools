#! /usr/bin/env python
from optparse import OptionParser

__author__ = 'andresantos'

class BiotoolScript(object):
    def __init__(self, args, root):
        self.__root = root
        self.__parser = OptionParser()
        self._build_parser(self.__parser)
        (self.__options, self.__args) = self.__parser.parse_args(args)
        self.__options = vars(self.__options)
        self._build()

    def _build_parser(self, parser):
        raise NotImplementedError("This method must be implemented")

    def _build(self):
        raise NotImplementedError("This method must be implemented")

    def _report(self):
        raise NotImplementedError("This method must be implemented")

    def _run(self):
        raise NotImplementedError("This method must be implemented")

    def run(self):
        self._run()
        self._report()

    def _get_option(self, key):
        return self.__options[key]

    def _has_option(self, key):
        return self.__options.has_key(key)

    def _get_arg(self, index):
        return self.__args[index]

    def _has_arg(self, index):
        return index < len(self.__args)

    def _root(self):
        return self.__root

    def _parser(self):
        return self.__parser

    @staticmethod
    def description():
        return "Abstract implementation of command line script"