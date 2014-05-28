#! /usr/bin/env python
from collections import deque
from fractions import gcd
import fractions
import itertools

from lib.interval import Interval
from lib.scripts.base_script import BaseScript
from lib.scripts.split_by_genotype import SplitByGenotypeWalker
from lib.walkers.vcf_walker import VCFWalker


__author__ = 'andresantos'

class SelectiveSweep (BaseScript):
    def _build_parser(self, parser):
        super(SelectiveSweep, self)._build_parser(parser)
        parser.add_option('-w', '--window', dest='window',
                          help='Sliding window size',
                          default=10000)
        parser.add_option('-s', '--step', dest='step',
                          help='Sliding window step size',
                          default=1000)
        parser.add_option('-k', '--kvcf', dest='kvcf',
                          help='1000 genomes vcf folder')

    def _build(self):
        super(SelectiveSweep, self)._build()
        self.__ipt = self._get_option('input')
        if self.__ipt is None:
            self._parser().error("You must inform a list of mutations "
                                 "and regions to evaluate")
        kvcf = self._get_option('kvcf')
        if kvcf is None:
            self._parser().error("You must inform the 1000 genomes VCF folder")
        self.__vcf = "%s/ALL.chr%s.phase1_release_v3.20101123.snps_indels_svs.genotypes.vcf.gz" % (kvcf, '%d')

        self.__window = int(self._get_option('window'))
        self.__step = int(self._get_option('step'))

        self.__bucks = gcd(self.__window, self.__step)

    def _run(self):
        for line in open(self.__ipt, 'r'):
            (chr, pos, rs, start, stop) = line.lstrip().split()
            mutation = Interval(chr, pos)
            rs = rs if rs != '.' else None
            split = SplitByGenotypeWalker(self.__vcf % int(chr),
                                          mutation,
                                          rsid=rs)
            split.walk()
            window = Interval(chr, start, stop)
            groups = {
                'HR' : split.get_hom_refs(),
                'HM' : split.get_hom_alts()
            }

            mtout = open("%s_%s_%s.sw" % (rs, chr, pos), 'w')
            dv = NucleotideDiversityWalker(self.__vcf % int(chr),
                                           window,
                                           groups=groups,
                                           window=self.__window, 
                                           step=self.__step,
                                           output=mtout)
            mtout.write("## PyBiotools - SelectiveSweep\n")
            mtout.write("## HR : %d\n" % len(groups['HR']))
            mtout.write("## HM : %d\n" % len(groups['HM']))
            print "Processing %s - %s" %(mutation, rs)
            if len(groups['HR']) <= 1  or len(groups['HM']) <= 1:
                mtout.write("## The groups must have at least 2 members\n")
            else:
                dv.walk()

class NucleotideDiversityWalker(VCFWalker):
    def _build_args(self, args):
        self.__total = 0
        # SAMPLING ARGS
        self.__samples = dict(args['groups'])
        self.__groups  = self.__samples.keys()
        self.__n = dict()
        for i in self.__groups:
            self.__n[i] = len(self.__samples[i])

        # WINDOW ARGS
        self.__at = self._interval().start()
        self.__window = int(args['window'])
        self.__step = int(args['step'])
        self.__bucket = fractions.gcd(self.__window, self.__step)
        self.__bck_window = self.__window/self.__bucket
        self.__bck_step = self.__step/self.__bucket
        self.__stacks = deque()
	self.__next_bucket()
        # Output
        if not args.has_key("output"):
            self.__output = open('%s_%s_%s.sw' % (self._interval().contig(),
                                               self._interval().start(),
                                               self._interval().stop()), 'w')
        else:
            self.__output = args["output"]

    def _reduce_init(self):
        return 0

    def _filter(self, record):
        return not record.is_snp

    def _map(self, record):
        for g in self.__groups:
            j = 0.0
            n = self.__n[g] * 2
            for sm in self.__samples[g]:
                call = record.genotype(sm)
                j += call.gt_type
            dv = 2 * j * (n-j) / (n * (n-1))
            if j > 0 and j < n:
                self.__append(record.POS, g, dv)
        return 1

    def __append(self, position, group, diversity):
        self.__move_to(position)
        self.__stacks[-1].append_snp(group, diversity)

    def __move_to(self, position):
        while self.__is_next_bucket(position):
            self.__next_bucket()
            if self.__is_next_window():
                self.__next_window()

    def __is_next_bucket(self, position):
        return self.__at + self.__bucket <= position

    def __next_bucket(self):
        self.__at += self.__bucket
        interval = self._interval().build(self.__at, self.__at + self.__bucket)
        self.__stacks.append(GroupWindow(interval, self.__groups))

    def __is_next_window(self):
        return len(self.__stacks) >= self.__bck_window

    def __next_window(self):
        acc = self.__stacks[0]
        for i in itertools.islice(self.__stacks, 1, self.__bck_window):
            #print acc.interval()
            #print i.interval()
            acc = acc.append(i)   
        self.__output.write("%s\n" % acc)
        for _ in range(self.__bck_step):
            self.__stacks.popleft()

    def _reduce(self, acc, cur):
        return acc + cur

    def _conclude(self, acc):
        self.__move_to(self._interval().stop())
        self.__next_window()
        self.__total = acc

    def evaluated(self):
        return self.__total


class GroupWindow (object):
    def __init__(self, interval, groups, diversity=None, nsnp=None):
        if isinstance(interval, Interval):
            self.__interval = interval
        else:
            self.__interval = Interval.factory(interval)

        self.__groups = groups
        if diversity is None:
            self.__diversity = dict.fromkeys(groups, 0)
        else:
            self.__diversity = diversity

        if nsnp is None:
            self.__nsnp = dict.fromkeys(groups, 0)
        else:
            self.__nsnp = nsnp

    def groups(self):
        return self.__groups

    def nsnp(self, group):
        return self.__nsnp[group]

    def diversity(self, group):
        return self.__diversity[group]

    def norm_diversity(self, group):
        return self.diversity(group)/self.interval().length()

    def interval(self):
        return self.__interval

    def append_snp(self, group, diversity):
        self.__nsnp[group] += 1
        self.__diversity[group] += diversity
        return self
	
    def append(self, other):
        interval  = self.interval() + other.interval()
        diversity = dict.fromkeys(self.groups(), 0)
        nsnp = dict.fromkeys(self.groups(), 0)
        for g in self.groups():
            diversity[g] = self.diversity(g) + other.diversity(g)
            nsnp[g] = self.nsnp(g) + other.nsnp(g)
        return GroupWindow(interval, self.groups(), diversity, nsnp)
    
    def __str__(self):
        it = self.interval()
        str = "%s\t%d\t%d\t" % (it.contig(), it.start(), it.stop())
        for g in self.groups():
            str += "%s\t%d\t%.5e\t" % (g, self.nsnp(g), self.norm_diversity(g))
        return str
