#! /usr/bin/env python
import MySQLdb
import math
from lib.interval import Interval
from lib.scripts.split_by_genotype import SplitByGenotypeWalker
from lib.utils.kg_vcf_utils import KGVCFUtils
from lib.walkers.base_walker import BaseWalker
from lib.walkers.simulation_walker import SimulationWalker
from lib.walkers.variant_counter import VariantCounter

__author__ = 'andresantos'

class RegionSimulationWalker(BaseWalker):
    # Database access
    DBACESS = {"host": "192.168.0.1",
               "port": 3306,
               "user": "andremr",
               "passwd": "13vI0U54",
               "db": "hapmap"}

    # Populations TAGS
    POP_AMR = "AMR"
    POP_ASN = "ASN"
    POP_AFR = "AFR"
    POP_EUR = "EUR"
    POPULATIONS = [POP_AFR, POP_ASN, POP_EUR]

    def __init__(self, input, kgfolder, **kwargs):
        super(RegionSimulationWalker, self).__init__(input, **kwargs)
        self.__kgutil = KGVCFUtils(kgfolder)
        # Init mysql Access
        self.__db = MySQLdb.connect(
            host=RegionSimulationWalker.DBACESS['host'],
            port=RegionSimulationWalker.DBACESS['port'],
            user=RegionSimulationWalker.DBACESS['user'],
            passwd=RegionSimulationWalker.DBACESS['passwd'],
            db=RegionSimulationWalker.DBACESS['db'])

    def __split_genotype(self, chr, pos, rs, vcf):
        rs = rs if rs != '.' else None
        mutation = Interval(chr, pos)

        split = SplitByGenotypeWalker(vcf, mutation, rsid=rs)
        split.walk()

        samples = list()
        frequency = 0.0
        for sample in split.get_hom_refs():
            macro = self.__kgutil.macro_population(sample)
            if macro != RegionSimulationWalker.POP_AMR:
                samples.append(sample)
        for sample in split.get_hom_alts():
            macro = self.__kgutil.macro_population(sample)
            if macro != RegionSimulationWalker.POP_AMR:
                samples.append(sample)
                frequency += 1

        return [samples, frequency]

    def __count_variants(self, chr, start, stop, vcf, samples):
        it = Interval(chr, start, stop)
        dv = VariantCounter(vcf, it, samples=samples)
        dv.walk()
        return dv.evaluated()

    def __compute_recombination(self, start, stop):
        query = "SELECT MIN(position), cm FROM recombination WHERE contig='chr%d' AND position >= %d"
        cursor = self.__db.cursor()
        cursor.execute(query % (int(chr), int(start)))
        low = float(cursor.fetchall()[0][1])
        cursor.execute(query % (int(chr), int(stop)))
        up = float(cursor.fetchall()[0][1])
        cursor.close()
        recombination_morgan = (up - low) / 100
        return .5 * (1 - math.exp(-recombination_morgan))

    def _map(self, record):
        (chr, pos, rs, start, stop) = record.lstrip().split()

        # Get VCF path
        vcf = self.__kgutil.get_vcf_path(chr)

        # Split samples by genotype
        samples, frequency = self.__split_genotype(chr, pos, rs, vcf)
        size = len(samples)
        frequency /= size

        # Prepare population attr
        macro_populations = dict.fromkeys(RegionSimulationWalker.POPULATIONS, 0)
        for sample in samples:
            macro_populations[self.__kgutil.macro_population(sample)] += 1

        # Count the number of variants
        variants = self.__count_variants(chr, start, stop, vcf, samples)

        # Compute recombination rate according to hapmap
        recombination = self.__compute_recombination(start, stop)

        # Simulate
        simulation = SimulationWalker(size, variants, frequency, macro_populations, recombination)
        simulation.walk()
        diversity_range = simulation.diversity()
        for mr, rr, dv in diversity_range:
            # CHR POS RS START END MR RR DV
            print "{:} {:} {:} {:} {:} {:} {:} {:}".format(chr, pos, start, stop, mr, rr, dv)
        return 1

    def evaluated(self):
        return self.__evaluated