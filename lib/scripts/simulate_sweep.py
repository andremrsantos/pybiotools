#! /usr/bin/env python
import MySQLdb
import math
from lib.interval import Interval
from lib.scripts.base_script import BaseScript
from lib.scripts.split_by_genotype import SplitByGenotypeWalker
from lib.vcf_walker import VCFWalker

__author__ = 'andresantos'

class SimulateSweep(BaseScript) :
    def _build_parser(self, parser):
        super(SimulateSweep, self)._build_parser(parser)
        parser.add_option('-k', '--kvcf', dest='kvcf', 
                          help='1000 genomes vcf folder')

    def _build(self):
        super(SimulateSweep, self)._build()
        # Get PATH for the list of mutations to investigate
        self.__ipt = self._get_option('input')
        
        if self.__ipt is None:
            self._parser().error("You must inform a list of mutations "
                                 "and regions to evaluate")
        # Verify PATH to 1KG variant folder
        self.__kvcf = self._get_option('kvcf')
        if self.__kvcf is None:
            self._parser().error("You must inform the 1000 genomes VCF folder")
        # Produce base PATH for VCF file
        self.__vcf = "%s/ALL.chr%s.phase1_release_v3.20101123." \
                     "snps_indels_svs.genotypes.vcf.gz" % (self.__kvcf, '%d')

    def _run(self):
        # Init mysql Acess
        db = MySQLdb.connect(host = "localhost",
                                    port = "3306",
                                    user = "andremr",
                                    passwd = "13vI0U54",
                                    db = "hapmap")
        cursor = db.cursor()

        # Load samples POP
        samples = dict()
        pops = list()
        for line in open('%s/phase1_integrated_calls.20101123.ALL.panel', 'r') :
            (smid, pop) = line.lstrip().split()[0:2]
            samples[smid] = pop
            if not pops.__contains__(pop):
                pops.append(pop)

        for line in open(self.__ipt, 'r'):
            (chr, pos, rs, start, stop) = line.lstrip().split()
            # Init mutation position
            mutation = Interval(chr, pos)
            rs = rs if rs != '.' else None

            # Divide samples according to the investigated mutation genotype
            split = SplitByGenotypeWalker(self.__vcf % int(chr), mutation,
                                          rsid=rs)
            split.walk()

            # Dividing samples and count pop
            sminv = split.get_hom_refs() + split.get_hom_alts()
            n = len(sminv)
            countpop = dict.fromkeys(pops, 0)
            for smid in sminv:
                countpop[samples[smid]] += 1
            npop = ' '.join(map(str, countpop.values()))

            # Count the number of variants
            window = Interval(chr, start, stop)
            dv = VariantCounter(self.__vcf % int(chr), window, samples=sminv)
            dv.walk()
            variants = dv.evaluated()

            # Compute recombination rate according to hapmap
            cursor.query("SELECT MIN(position), cm "
                              "FROM recombination "
                              "WHERE contig='chr%d' "
                              "AND position >= %d", (int(chr), int(start)))
            lw = cursor.fetchall()[0][1]
            cursor.query("SELECT MIN(position), cm "
                              "FROM recombination "
                              "WHERE contig='chr%d' "
                              "AND position >= %d", (int(chr), int(stop)))
            up = cursor.fetchall()[0][1]
            m = (up - lw) / 100
            r = .5 * (1 - math.log(-m))
            p = 4 * n * r

            # mount ms script
            script = "ms %d %d -s %d -r %f -I %s" % (2*n, 10000, variants + 1, p, npop)
            print script



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