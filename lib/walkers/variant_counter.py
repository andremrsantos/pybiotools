#! /usr/bin/env python
from lib.walkers.vcf_walker import VCFWalker

__author__ = 'andresantos'

class VariantCounter(VCFWalker):
    def _build_args(self, args):
        # SAMPLING ARGS
        self.__samples = args['samples']
        self.__n = len(self.__samples)

    def _reduce_init(self):
        return 0

    def _filter(self, record):
        return not record.is_snp

    def _map(self, record):
        j = 0
        n = 2 * self.__n

        for sm in self.__samples:
            call = record.genotype(sm)
            j += call.gt_type

        if j > 0 and j < n:
            return 1
        else:
            return 0

    def _reduce(self, acc, cur):
        return acc + cur

    def _conclude(self, acc):
        self.__total = acc

    def evaluated(self):
        return self.__total