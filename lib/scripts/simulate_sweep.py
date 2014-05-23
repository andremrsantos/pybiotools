#! /usr/bin/env python
from multiprocessing.queues import Queue
import threading
import time
import MySQLdb
import math
import sys
from lib.interval import Interval
from lib.scripts.base_script import BaseScript
from lib.scripts.split_by_genotype import SplitByGenotypeWalker
from lib.vcf_walker import VCFWalker
from lib.utils.kg_vcf_utils import KGVCFUtils

__author__ = 'andresantos'

class SimulateSweep(BaseScript):

    def _build_parser(self, parser):
        super(SimulateSweep, self)._build_parser(parser)
        parser.add_argument('-n', '--thread',
                            dest='nt', type=int,
                            help='Number of running threads')
        KGVCFUtils.add_argument(parser)

    def _build(self):
        super(SimulateSweep, self)._build()
        self.__walker = RegionWalker(self._get_option('input'),
                                     self._get_option('kvcf'),
                                     self._get_option('nt'))

    def _run(self):
        self.__walker.walk()


class RegionWalker(object):
    # Database access
    DBACESS = {"host": "localhost",
               "port": 3306,
               "user": "andremr",
               "passwd": "13vI0U54",
               "db": "hapmap"}

    # Migration Rate
    MU = 0.013

    # Populations TAGS
    POP_AMR = "AMR"
    POP_ASN = "ASN"
    POP_AFR = "AFR"
    POP_EUR = "EUR"
    POPULATIONS = [POP_AFR, POP_ASN, POP_EUR]

    def __init__(self, input_list, kgfolder, nthread=1):
        self.__kgutil = KGVCFUtils(kgfolder)

        # Init mysql Access
        db = MySQLdb.connect(host=RegionWalker.DBACESS['host'],
                             port=RegionWalker.DBACESS['port'],
                             user=RegionWalker.DBACESS['user'],
                             passwd=RegionWalker.DBACESS['passwd'],
                             db=RegionWalker.DBACESS['db'])
        self.__db_cursor = db.cursor()

        # Set thread parameters
        self.__nthread = nthread
        self.__lock = threading.Lock()
        self.__queue = Queue()
        for line in open(input_list, 'r'):
            self.__queue.put(line)
        self.__total = self.__queue.qsize()

    def _reduce_init(self):
        return 0

    def walk(self):
        self.__acc = self._reduce_init()
        # Starting threads
        self.__threads = list()
        for i in range(self.__nthread):
            thread = threading.Thread(target=self._run)
            thread.daemon = True
            thread.start()
            self.__threads.append(thread)
        while threading.activeCount() > 1:
            time.sleep(1)
            rate = self.__acc * 100.0/self.__total
            sys.stderr.write("%05d / %05d = %03.2f %\d" % (self.__acc, self.__total, rate))
            sys.stderr.flush()
        self._conclude(self.__acc)

    def _run(self):
        while not self.__queue.empty():
            record = self.__queue.get()
            cur = self._map(record)
            self.__lock.acquire()
            self.__acc = self._reduce(self.__acc, cur)
            self.__lock.release()

    def _map(self, record):
        (chr, pos, rs, start, stop) = record.lstrip().split()

        # VCFPATH
        vcf = self.__kgutil.get_vcf_path(chr)

        # Init mutation position
        mutation = Interval(chr, pos)
        rs = rs if rs != '.' else None

        # Divide samples according to the investigated mutation genotype
        split = SplitByGenotypeWalker(vcf, mutation, rsid=rs)
        split.walk()

        # Dividing samples filtering AMR and compute mutation frequency
        samples = list()
        frequency = 0
        for sample in split.get_hom_refs():
            if self.__kgutil.macro_population(sample) != 'AMR':
                samples.append(sample)
        for sample in split.get_hom_alts():
            if self.__kgutil.macro_population(sample) != 'AMR':
                frequency += 1
                samples.append(sample)

        size = len(samples)
        frequency /= size

        # Prepare population attr
        macro_populations = dict.fromkeys(RegionWalker.POPULATIONS, 0)
        for sample in samples:
            macro_populations[self.__kgutil.macro_population(sample)] += 2
        migration_rate = 4*size*RegionWalker.MU
        pop_attr = "3 {:} {:}".format(
            ' '.join(map(str, macro_populations.values())),
            migration_rate)

        # Count the number of variants
        dv = VariantCounter(vcf, Interval(chr, start, stop), samples=samples)
        dv.walk()
        variants = dv.evaluated()

        # Compute recombination rate according to hapmap
        query = "SELECT MIN(position), cm FROM recombination WHERE contig='chr%d' AND position >= %d"
        self.__db_cursor.execute(query %  (int(chr), int(start)))
        start = float(self.__db_cursor.fetchall()[0][1])
        self.__db_cursor.execute(query % (int(chr), int(stop)))
        stop = float(self.__db_cursor.fetchall()[0][1])
        recombination_morgan = (start - stop) / 100
        recombination_rate = .5 * (1 - math.exp(-recombination_morgan))
        recombination = 4 * size * recombination_rate

        # mount ms script
        script = "{0:} {1:} {2:} -s {3:} -r {4:} {3:} -I {5:}".format(
            "~/src/ms/msdir/ms", 2*size, 10000, variants+1, recombination, pop_attr)
        self._print(script)

    def _print(self, string):
        self.__lock.acquire()
        print string
        self.__lock.release()

    def _reduce(self, acc, cur):
        return acc + cur

    def _conclude(self, acc):
        self.__total = acc

    def evaluated(self):
        return self.__total

class VariantCounter(VCFWalker) :
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
