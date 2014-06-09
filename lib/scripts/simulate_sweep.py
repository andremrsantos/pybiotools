#! /usr/bin/env python
from Queue import Queue
import threading
import time
import math
import sys

import MySQLdb

from lib.interval import Interval
from lib.scripts.base_script import BaseScript
from lib.scripts.split_by_genotype import SplitByGenotypeWalker
from lib.utils.kg_vcf_utils import KGVCFUtils
from lib.walkers.region_simulation_walker import RegionSimulationWalker


__author__ = 'andresantos'

MySQLdb.threadsafety = 2


class SimulateSweep(BaseScript):
    def _build_parser(self, parser):
        super(SimulateSweep, self)._build_parser(parser)
        KGVCFUtils.add_argument(parser)

    def _build(self):
        super(SimulateSweep, self)._build()
        self.__walker = RegionSimulationWalker(
            self._get_option('input'),
            self._get_option('kvcf')
        )

    def _run(self):
        self.__walker.walk()

    def _report(self):
        print "Ended..."
