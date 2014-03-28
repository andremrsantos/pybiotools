#! /usr/bin/env python

__author__ = 'andresantos'

import vcf

class VCFWalker(object):
    def __init__(self, input, interval=None, **args):
        self.__iterator = vcf.Reader(open(input, 'r'))
        self.__interval = interval

        if self.__interval is not None:
            self.__iterator = self.__iterator.fetch(self.__interval.contig(),
                                                  self.__interval.start(),
                                                  self.__interval.stop())
        self._build_args(args)

    def _build_args(self, args):
        pass

    def walk(self):
        acc = self._reduce_init()
        for record in self.__iterator:
            if not self._filter(record):
                cur = self._map(record)
                acc = self._reduce(acc, cur)
        self._conclude(acc)

    def _map(self, record):
        raise NotImplemented("Must be implemented")

    def _filter(self, record):
        ## Takes an record and filter
        return False

    def _reduce_init(self):
        # init reduce value
        return 0

    def _reduce(self, acc, cur):
        ## Takes current map result and merge to the acc
        raise NotImplemented("Must be implemented")

    def _conclude(self, acc):
        # close the result processing
        pass

    def progress(self):
        current = self.__iterator.POS
        max = self.__interval.stop()
        length = self.__interval.length()
        return (max - current) / length
