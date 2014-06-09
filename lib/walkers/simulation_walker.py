#! /usr/bin/env python
import re
import subprocess
from lib.walkers.base_walker import BaseWalker

__author__ = 'andresantos'

class SimulationWalker(BaseWalker):
  # MS
  MS_PATH = "/home/andremr/src/ms/msdir/ms"

  # Migration Rate
  MU = 0.013

  def __init__(self, size, variants, frequency, macro_count, recombinations, repetitions=10000, **kwargs):
    script = self.mount_script(size, variants, macro_count, recombinations, repetitions)
    #print script
    process = subprocess.Popen(script.split(), stdout=subprocess.PIPE)
    self._set_iterator(process.stdout)
    self.__total = repetitions
    self.__group = list()
    self.__count = 0
    self.__diversity = []
    self.__size = size
    self.__variants = variants
    self.__frequency = frequency * 2 * size
    self._build_args(kwargs)

  def mount_script(self, size, variants, macro_count, recombinations, repetions):
    pop_line = "{:} {:} {:}".format(
      len(macro_count),
      ' '.join([str(i * 2) for i in macro_count.values()]),
      4 * size * SimulationWalker.MU
    )
    rrate = 4 * size * recombinations
    return "{0:} {1:} {2:} -s {3:} -r {4:} {3:} -I {5:}".format(
      SimulationWalker.MS_PATH, 2 * size, repetions, variants+1, rrate, pop_line
    )

  def _filter(self, record):
    return re.search('^[a-zA-Z]', record, flags=re.I)

  def __compute_frequency(self, group, start, stop):
    fq = [0 for _ in xrange(start, stop)]
    n = len(group)
    # print '%d -- %d  (%d) --> %s' % (start, stop, len(group[0]), group[0])
    for line in group:
      for position in xrange(start, stop):
        if line[position] == '1':
          fq[position-start] += 1.0
    return fq

  def __compute_rate(self, group, index):
    group_mut = [line for line in group if line[index] == '1']
    mutrate = self.__compute_diversity(group_mut)
    group_ref = [line for line in group if line[index] == '0']
    refrate = self.__compute_diversity(group_ref)
    return [len(group_mut), mutrate, len(group_ref), refrate, mutrate/refrate]

  def __compute_diversity(self, group):
    count = [1E-12 for _ in group[0]]
    n = len(group)
    # print n
    for ind in group:
      for i in xrange(0, len(ind)):
        if ind[i] == '1':
          count[i] += 1
    return sum([2.0*j*(n-j)/(n*(n-1)) for j in count])

  def __select_index(self, middle, goal):
    idx = 0
    current = middle[0]
    threshold = 1.0/self.__size
    # print self.__is_valid(current, threshold)
    for i in xrange(1,len(middle)):
      av = middle[i]
      if not self.__is_valid(current, threshold) or (self.__is_closer(av, current, goal) and self.__is_valid(av, threshold)) :
        idx = i
        current = middle[i]
    #print current
    return idx

  def __maf(self, frequency) :
    return min(frequency, 1 - frequency)

  def __distance(self, value, goal):
    return abs(value - goal)

  def __is_closer(self, one, other, goal):
    return self.__distance(one, goal) < self.__distance(other, goal)

  def __is_valid(self, one, threshold=0):
    # print one/self.__size/2
    return self.__maf(one/self.__size/2) > threshold

  def _map(self, record):
    # print record
    if re.search('^\/\/', record):
      # print "Here"
      self.__group = list()
      self.__count += 1
    elif re.search('^[01]+$', record):
      self.__group.append(record.lstrip())
    elif re.search('^\s', record) and len(self.__group) > 0:
      start = self.__variants/4
      stop = start + self.__variants/2
      middle = self.__compute_frequency(self.__group, start, stop)
      index = start + self.__select_index(middle, self.__frequency)
      # print index
      rate = self.__compute_rate(self.__group, index)
      print "\t".join(map(str, rate))
      return 1
    
    return 0

  def diversity(self):
    return self.__diversity[:]
