from pybiotools.helpers import io_helper
from re import match


class FileIterator(object):
    def __init__(self, fname):
        self.__fpath = fname
        self.__finput = open(fname, 'r')
        self.__flen = io_helper.line_number(fname)
        self.__current_line = 0

    def file_path(self):
        return self.__fpath

    def len(self):
        return self.__flen

    def at(self):
        return self.__current_line

    def next(self):
        self.__current_line += 1
        return self.__finput.readline().rstrip()

    def has_next(self):
        return self.at() <= self.len()

    def read_progress(self):
        return float(self.at())/float(self.len())

    def info(self):
        return "[{:02.2f}%] {:} at '{:}' at line {:d} of {:d}.".format(
            self.read_progress()*100, self.__class__.__name__,
            self.file_path(), self.at(), self.len())