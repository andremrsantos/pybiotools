#! /usr/bin/env python
import sys
from datetime import datetime

__author__ = 'andresantos'

class LogUtils(object):
    def __init__(self, script):
        self.__output = sys.stderr
        self.__script = script
        self.__script_name = script.__class__.__name__
        self._starting()

    def _starting(self):
        self._logging("Starting %s processing..." % self.__script_name)

    def _logging(self, string):
        log = "## {0:} -- {1:}\n".format(datetime.now(), string)
        self.__write(log)

    def _logging_progress(self):
        self._logging(self.__script.progress())

    def __write(self, string):
        self.__output.write(string)
        self.__output.flush()