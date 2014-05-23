import os
import re
import subprocess
import warnings

from lib.scripts.biotoolscript import BiotoolScript
from lib.interval import Interval


class SplitByGenotypeBcftools(BiotoolScript):
    def _build_parser(self, parser):
        parser.set_description("Usage: %prog SplitByGenotypeBcftools [options]")
        parser.add_option('-l','--interval', dest='interval',
                          help='Mutation genomic interval')
        parser.add_option('-c','--contig', dest='contig',
                          help='Mutation contig')
        parser.add_option('-p','--position', dest='position',
                          help='Mutation chromosome position')
        parser.add_option('-r','--id', dest='rsid',
                          help='Mutation ID tag')
        parser.add_option('-B', '--bcftools-path', dest='bcftools',
                          help='interval reference build',
                          default="bcftools")
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
        rsid= self._get_option('rsid')
        input= self._get_option('input')
        bcftools = self._get_option('bcftools')
        ref_build= self._get_option('reference')

        self.__output = "%d.sbgb.tmp" % os.getpid()
        self.__script = "{} query -f '[%ID %SAMPLE %GT\\n]' -r {} {} {} > {}"

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
        filter = ''
        if rsid is not None or rsid=='.':
            filter = " | grep -w '%s'" % rsid
        ## Init processing walker
        if input is not None:
            self.__script = self.__script.format(bcftools, self.__interval,
                                                 input, filter, self.__output)
        else:
            self._parser().error("Must inform an VCF input file (-i)")

    @staticmethod
    def description():
        return "Split the VCF samples according to their genotypes of a " \
               "certain mutation"

    def run(self):
        ## Extract by BCFTOOLS samples genotype
        subprocess.call(self.__script, shell=True)
        self.__groups = {'00': [], '01': [], '11': [], '.': []}
        for line in open(self.__output, 'r'):
            (sm, gt) = re.sub(r"[/\|]", '', line.lstrip()).split()[1:]
            if gt == '00':
                self.__groups['00'].append(sm)
            elif gt == '01' or gt == '10':
                self.__groups['01'].append(sm)
            elif gt == '11':
                self.__groups['11'].append(sm)
            elif gt == '..' or gt == '.':
                self.__groups['.'].append(sm)
            else:
                warnings.warn("Unrecognized genotype '%s' for sample %s" %
                              (gt, sm))
        subprocess.call("rm %s" % self.__output, shell=True)
        self.__print_report()

    def __print_report(self):
        print "## Split by Genotype"
        print "## VCF input: %s" % self._get_option('input')
        print "## Locus:     %s" % self.__interval
        print "## ID:        %s" % self._get_option('rsid') or '.'
        print "## N00: %5d" % len(self.__groups['00'])
        print "## N01: %5d" % len(self.__groups['01'])
        print "## N11: %5d" % len(self.__groups['11'])
        print "## N. : %5d" % len(self.__groups['.'])
        print "00 : [%s]" % ",".join(self.__groups['00'])
        print "01 : [%s]" % ",".join(self.__groups['01'])
        print "11 : [%s]" % ",".join(self.__groups['11'])
        print ".  : [%s]" % ",".join(self.__groups['.'])
