#! /usr/bin/env python
import sys

__author__ = 'andresantos'

class Bootstrap(object):
    def __init__(self, interactions, simulator):
        self.__interactions = interactions
        self.__current = 0
        self.__simulator = simulator

    def run(self):
        while self.__current < self.__interactions:
            self.__simulator.simulate()
            self.__current += 1
            self.print_progress()


    def progress(self):
        return float(self.__current)/self.__interactions

    def print_progress(self):
        sys.stdout.write("\r%3.3f" % (self.progress()*100))
        sys.stdout.flush()