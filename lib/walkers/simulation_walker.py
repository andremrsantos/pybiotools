#! /usr/bin/env python
import re
import subprocess
from lib.walkers.base_walker import BaseWalker

__author__ = 'andresantos'

class SimulationWalker(BaseWalker):
    # MS
    MS_PATH = "~/src/ms/msdir/ms"

    # Migration Rate
    MU = 0.013

    def __init__(self, size, variants, frequency, macro_count,
                 recombinations, repetitions=10000, **kwargs):
        script = self.mount_script(size, variants, macro_count, recombinations,
                                   repetitions)
        process = subprocess.Popen(script, stdout=subprocess.PIPE)
        simulation = process.communicate()[0].splitlines()
        self.__iterator = iter(simulation)
        self.__total = len(simulation)
        self.__group = None
        self.__count = 0
        self.__diversity = []
        self.__size = size
        self.__variants = variants
        self.__frequency = frequency
        self.__buil_args(kwargs)

    def mount_script(self, size, variants, macro_count,
                     recombinations, repetions):
        pop_line = "{:} {:} {:}".format(
            len(macro_count),
            ' '.join(map(str, macro_count.values())),
            4 * size * SimulationWalker.MU
        )
        rrate = 4 * size * recombinations
        return "{0:} {1:} {2:} -s {3:} -r {4:} {3:} -I {5:}".format(
            SimulationWalker.MS_PATH, size, repetions, variants+1, rrate, pop_line
        )

    def _filter(self, record):
        return re.search('^[a-zA-Z]', record, flags=re.I)

    def __compute_frequency(self, group, start, stop):
        fq = [0 for _ in xrange(start, stop)]
        n = len(group)
        for line in group:
            for position in xrange(start, stop):
                if line[position] == '1':
                    fq[position] += 1.0/n
        return fq

    def __compute_rate(self, group, index):
        group_mut = [line for line in group if line[index] == '1']
        mutrate = self.__compute_diversity(group_mut)
        group_ref = [line for line in group if line[index] == '0']
        refrate = self.__compute_diversity(group_ref)
        return [mutrate, refrate, mutrate/refrate]
    def __compute_diversity(self, group):
        count = [0 for _ in group[0]]
        n = len(group)
        for ind in group:
            for i in xrange(0, len(ind)):
                if ind[i] == '1':
                    count[i] + 1

        return sum([2.0*j*(n-j)/(n*(n-1)) for j in count])

    def _map(self, record):
        if re.search('^\/\/', record):
            self.__group = list()
            self.__count += 1
        elif re.search('^[01]', record):
            self.__group.append(record.lstrip())
        elif re.search('^\s', record) and self.__group is not None:
            start = self.__variants/4
            stop = start + self.__variants/2
            middle = self.__compute_frequency(self.__group, start, stop)
            min = 0
            for i in xrange(1,len(middle)):
                if abs(middle[min] - self.__frequency) > abs(middle[i] - self.__frequency):
                    min = i
            index = start + min
            self.__diversity.append(self.__compute_rate(self.__group, index))

    def diversity(self):
        return self.__diversity[:]