#! /usr/bin/env python
from os import sysconf
import os
from lib.utils.log_utils import LogUtils

__author__ = 'andresantos'

class BaseWalker(object):
    def __init__(self, input, **kwargs):
        self._set_iterator(open(input, 'r'))
        self._build_args(kwargs)
        self.__total = int(os.popen('wc -l %s' % input).read().split()[0])

    def _set_iterator(self, iter):
        self.__iterator = iter

    def _build_args(self, args):
        pass

    def walk(self):
        self.__init()
        acc = self._reduce_init()
        while True:
            record = self.__next_record()
            if record is None:
                break
            if not self._filter(record):
               cur = self._map(record)
               acc = self._reduce(acc, cur)
        self._conclude(acc)
        return self

    def __init(self):
        self.__log = LogUtils(self)
        self.__at = 1

    def __next_record(self):
        self.__at += 1
        return next(self.__iterator, None)

    def _reduce_init(self):
        return 1

    def _reduce(self, acc, current):
        return acc + current

    def _filter(self, record):
        pass

    def _map(self, record):
        raise NotImplementedError('You must implement \'_map\' method')

    def _conclude(self, acc):
        self.__iterator.close()
        self.__evaluated = acc

    def progress(self):
        return self.__at * 100.0 / self.__total

    def log_progress(self):
        name = self.__class__.__name__
        rate = self.progress()
        return "{:} progress: {:}% -- Processing line {:} of {:}".format(
            name, rate, self.__at, self.__total)

    def _logger(self):
        return self.__log
