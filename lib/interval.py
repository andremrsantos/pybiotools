#! /usr/bin/env python

__author__ = 'andresantos'

import lib.reference as reference
import inspect
import re

class Interval(object):
    __reference = reference.b37

    @staticmethod
    def available_references():
        return [k for k,x in inspect.getmembers(reference)
                if inspect.isclass(x)]

    @staticmethod
    def set_reference(ref):
        available = Interval.available_references()
        if ref in available:
            Interval.__reference = getattr(reference, ref)
        else:
            available = "  ".join(available)
            raise AttributeError("Invalid genome reference.\n"
                                 "Pick one of the following:\n%s" % available)

    @staticmethod
    def factory(interval):
        match = re.match(r'^(.+?)((:(\d+)((-(\d+))|))|)$',interval)
        return Interval(match.group(1), match.group(4), match.group(7))

    def __init__(self, chr=None, start=None, stop=None):
        self.__contig = chr
        min = self.contig_start(chr)
        max = self.contig_stop(chr)
        if start is None:
            self.__start = min
            self.__stop = max
        else:
            start = int(start)
            self.__start = start if start > 0 else min
            if stop is None:
                self.__stop = self.__start
            else:
                stop = int(stop)
                self.__stop = stop if stop < max else max
        self.__check_position()

    def build(self, start, stop=None):
        return Interval(self.contig(), start, stop)

    def contig(self):
        return self.__contig

    def start(self):
        return self.__start

    def stop(self):
        return self.__stop

    def length(self):
        return self.stop() - self.start()

    def internal(self, other):
        return self.same_contig(other) and \
               other.start() <= self.start() and other.stop() <= self.stop()

    def intersect(self, other):
        return self.same_contig(other) and \
               (other.start() <= self.start() or other.stop() <= self.stop())

    def before(self, other):
        return self.same_contig(other) and other.start < self.start()

    def after(self, other):
        return self.same_contig(other) and other.start > self.start()

    def same_contig(self, other):
        self.__check_class(other)
        return other.contig() == self.contig()

    def __check_class(self, other):
        if not isinstance(other, self.__class__):
            raise AttributeError("Invalid argument. You must pass an Interval")

    def __check_contig(self, other):
        self.__check_class()
        if self.same_contig(other):
            raise AttributeError("The intervals must be on the same contig")

    def __check_position(self):
        if self.stop() < self.start():
            raise AttributeError("The interval must have stop greater than start")

    def __add__(self, other):
        if not self.intersect(other):
            raise AttributeError("The intervals are not addable")
        elif self.before(other):
            return Interval(self.contig(), self.start(), other.stop())
        else:
            return Interval(self.contig(), other.start(), self.stop())

    def __sub__(self, other):
        if not self.intersect(other) :
            return self
        elif self.before(other):
            return Interval(self.contig(), other.stop(), self.start())
        else:
            return Interval(self.contig(), self.start(), other.start())

    def contig_start(self, contig):
        return Interval.__reference.CONTIGS[contig][0]

    def contig_stop(self, contig):
        return Interval.__reference.CONTIGS[contig][1]

    def __str__(self):
        interval = "%s:%d" % (self.contig(), self.start())
        if self.stop() != self.start():
            interval += "-%d" % self.__stop
        return interval