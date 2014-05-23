#! /usr/bin/env python

__author__ = 'andresantos'

class KGVCFUtils(object):

    @staticmethod
    def add_argument(parser):
        parser.add_argument('-k', '--kvcf', dest='kvcf', required=True,
                            help='1000 genomes genotype vcf folder')

    def __init__(self, folder):
        self.__folder = folder
        self.__load_sample_info()

    def get_vcf_path(self, chromossome):
        chromossome = int(chromossome)

        return "{0:}/ALL.chr{1:n}.*.genotypes.vcf.gz".format(self.__folder,
                                                             chromossome)

    def samples(self):
        return list(self.__samples)

    def samples_from(self, population):
        return [self.__population[sample]
                for sample in self.__population
                if self.__population[sample] == population]

    def samples_from_macro(self, macro):
        return [self.__macro_population[sample]
                for sample in self.__macro_population
                if self.__macro_population[sample] == macro]

    def population(self, sample):
        return self.__population[sample]

    def macro_population(self, sample):
        return self.__macro_population[sample]

    def __load_sample_info(self):
        panel = "{0:}/*.ALL.panel".format(self.__folder)

        self.__macro_population = dict()
        self.__population = dict()
        self.__samples = list()

        for line in open(panel, 'r'):
            (sample, population, macro) = line.lstrip().split()[0:3]
            self.__samples.append(sample)
            self.__population[sample] = population
            self.__macro_population[sample] = macro