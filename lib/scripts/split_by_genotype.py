#! /usr/bin/env python
from lib.interval import Interval

__author__ = 'andresantos'

from lib.scripts.biotoolscript import BiotoolScript
from lib.walkers.vcf_walker import VCFWalker

class SplitByGenotypeWalker(VCFWalker):
    def _build_args(self, args):
        self.__rsid = args['rsid']
        self.__record = None

    def _reduce_init(self):
        return 0

    def _filter(self, record):
        return record.ID != self.__rsid

    def _map(self, record):
        self.__record = record
        return 1

    def _reduce(self, acc, cur):
        return acc + cur

    def record(self):
        return self.__record

    def get_hom_refs(self):
        return [x.sample for x in self.record().get_hom_refs()]

    def get_hets(self):
        return [x.sample for x in self.record().get_hets()]

    def get_hom_alts(self):
        return [x.sample for x in self.record().get_hom_alts()]

    def get_unknowns(self):
        return [x.sample for x in self.record().get_unknowns()]

    def alleles(self):
        if self.record() is None:
            return ''
        return [x.__str__() for x in self.record().alleles]

class SplitByGenotype(BiotoolScript):
    def _build_parser(self, parser):
        parser.set_description("Usage: %prog SplitByGenotype [options]")
        parser.add_option('-l','--interval', dest='interval',
                          help='Mutation genomic interval')
        parser.add_option('-c','--contig', dest='contig',
                          help='Mutation contig')
        parser.add_option('-p','--position', dest='position',
                          help='Mutation chromosome position')
        parser.add_option('-r','--id', dest='rsid',
                          help='Mutation ID tag')
        parser.add_option('-R', '--reference', dest='reference',
                          help='interval reference build')
        parser.add_option('-i','--input', dest='input',
                          help='VCF file path')
        return parser

    def _build(self):
        ## Check position reference
        interval = self._get_option('interval')
        chr = self._get_option('contig')
        pos = self._get_option('position')
        rsid = self._get_option('rsid')
        input = self._get_option('input')
        ref_build = self._get_option('reference')

        ## Update genome reference build data if necessary
        if ref_build is not None:
            Interval.set_reference(ref_build)

        ## Set working locus
        if interval is not None:
            self.__interval = Interval.factory(interval)
        elif chr is not None and pos is not None:
            self.__interval = Interval(chr, pos)
        else:
            self._parser().error("Must inform either the mutation by "
                                 "the genomic interval (-l) or "
                                 "the contig (-c) and position (-p)")

        rsid = rsid if rsid=='.' else None

        ## Init processing walker
        if input is not None:
            self.__walker = SplitByGenotypeWalker(input, self.__interval,
                                                  rsid=rsid)
        else:
            self._parser().error("Must inform an VCF input file (-i)")

    @staticmethod
    def description():
        return "Split the VCF samples according to their genotypes of a " \
               "certain mutation"

    def run(self):
        self.__walker.walk()
        self.__print_report()

    def __print_report(self):
        print "## Split by Genotype"
        print "## VCF input: %s" % self._get_option('input')
        print "## Locus:     %s" % self.__interval
        print "## ID:        %s" % self._get_option('rsid') or '.'
        print "## ALLELES:   %s" % ",".join(self.__walker.alleles())
        print "## N00: %5d" % self.__walker.record().num_hom_ref
        print "## N01: %5d" % self.__walker.record().num_het
        print "## N11: %5d" % self.__walker.record().num_hom_alt
        print "## N. : %5d" % self.__walker.record().num_unknown
        print "00 : [%s]" % ",".join(self.__walker.get_hom_refs())
        print "01 : [%s]" % ",".join(self.__walker.get_hets())
        print "11 : [%s]" % ",".join(self.__walker.get_hom_alts())
        print ".  : [%s]" % ",".join(self.__walker.get_unknowns())
