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
        self.log("Starting %s processing..." % self.__script_name)

    def log(self, string):
        log = "## {0:} -- {1:}\n".format(datetime.now(), string)
        self.__write(log)

    def log_progress(self):
        self.log(self.__script.log_progress())

    def __write(self, string):
        self.__output.write(string)
        self.__output.flush()
