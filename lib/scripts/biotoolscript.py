#! /usr/bin/env python
from argparse import ArgumentParser

__author__ = 'andresantos'

class BiotoolScript(object):
    def __init__(self, args, root, description=""):
        self.__root = root
        self.__parser = ArgumentParser(description=description)
        self._build_parser(self.__parser)
        self.__options = self.__parser.parse_args(args)
        self.__options = vars(self.__options)
        self._build()

    def _build_parser(self, parser):
        pass

    def _build(self):
        pass

    def _report(self):
        raise NotImplementedError("This method must be implemented")

    def _run(self):
        raise NotImplementedError("This method must be implemented")

    def run(self):
        self._run()
        self._report()

    def _get_option(self, key):
        return self.__options[key]

    def _get_arg(self, index):
        return self.__args[index]

    def _root(self):
        return self.__root

    def _parser(self):
        return self.__parser

    @staticmethod
    def description():
        return "Abstract implementation of command line script"