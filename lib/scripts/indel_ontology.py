#! /usr/bin/env python
import random

from lib.scripts.db_script import DBScript
from lib.simulation.bootstrap import Bootstrap

__author__ = 'andresantos'

class OntologyTerm:
    def __init__(self, goid, term, n, list = None):
        self.goid = goid
        self.term = term
        self.n = n
        self.list = list

    def __str__(self):
        return ("%s\t%05d\t(%s)\t%s" % (self.goid, self.n, self.list, self.term))

class IndelOntology(DBScript):
    def _build_parser(self, parser):
        super(IndelOntology, self)._build_parser(parser)
        parser.set_defaults(dbname='geneontology')
        parser.add_option('-s', '--simulate', dest='simulate',
                          help='Number of bootstrap interactions to perform',
                          default=1000)
        parser.add_option('-c', '--cutoff', dest='pvalue',
                          help='p-value cutoff',
                          default=0.1)
        parser.add_option('-g', '--group', dest='group',
                          help='Ontology group [F or P]',
                          default='p')

    def _build(self):
        super(IndelOntology, self)._build()
        ipt = self._get_option('input')
        if ipt is None:
            self._parser().error("You must inform a list of indels to evaluate")

        self.__simulate = int(self._get_option('simulate'))
        self.__pvalue = float(self._get_option('pvalue'))
        self.__group = self._get_option('group')
        self.__universe = [int(x[0]) for x in self._query("SELECT DISTINCT id "
                                                         "FROM indelk_gene")]
        self.__indels = [int(x.lstrip()) for x in open(ipt, 'r')
                         if int(x.lstrip()) in self.__universe]
        self.__n = len(self.__indels)

        self.__simulation = Bootstrap(self.__simulate, self)

    def _run(self):
        self.base_ontology = self.__query_ontology(self.__indels, self.__group)
        self.pvalue = dict.fromkeys(self.base_ontology.keys(), 0)

        self.__simulation.run()

    def __sample(self):
        random.shuffle(self.__universe)
        return self.__universe[0:self.__n]

    def __query_ontology(self, indels, group):
        result = {}
        query = "SELECT COUNT(DISTINCT id), a.goid, term " \
                "FROM ontology_data a, ontology_definition b, indelk_gene c " \
                "WHERE a.goid=b.goid AND ontology=%s AND a.gene=c.gene AND " \
                "  id IN (%s) " \
                "GROUP BY a.goid" % ('%s', ','.join(['%s' for x in indels]))

        for entry in self._query(query, group, indels):
            result[entry[2]] = OntologyTerm(entry[1], entry[2],
                                            entry[0], None)
        # query = "SELECT DISTINCT id, a.goid, term " \
        #         "FROM ontology_data a, ontology_definition b, indelk_gene c " \
        #         "WHERE a.goid = b.goid AND a.gene = c.gene AND " \
        #         "  id = %s AND ontology = %s"
        # for indel in indels:
        #     for entry in self._query(query, indel, group):
        #         (goid, term) = entry[1:]
        #         if result.has_key(goid):
        #             result[goid].n += 1
        #             result[goid].list.append(indel)
        #         else:
        #             result[goid] = OntologyTerm(goid, term, 0, [])
        return result

    def __evaluate(self, ontology):
        for key in self.base_ontology.keys():
            if ontology.has_key(key) and \
                            ontology[key].n >= self.base_ontology[key].n:
                self.pvalue[key] += 1.0/self.__simulate

    def simulate(self):
        sample = self.__sample()
        ontology = self.__query_ontology(sample, self.__group)
        self.__evaluate(ontology)

    def _report(self):
        keys = sorted(self.pvalue, key=self.pvalue.__getitem__)
        print "## Indel Ontology"
        print "## Indels evaluated: %d" % self.__n
        print "## Ontologies found: %d" % len(keys)
        print "## PVALUE\tGOID\tN\tindels\tontology"
        for k in keys:
            if self.pvalue[k] <= self.__pvalue:
                print "%1.4f\t%s" % (self.pvalue[k], self.base_ontology[k])
            else:
                break

    def progress(self):
        return self.__simulation.progress()
