from sys import stderr
from time import gmtime, strftime
from threading import Timer


def current_timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


class Logger(object):
    def __init__(self, interval=10, output=stderr):
        self.__interval = interval
        self.__output = output
        self.__timer = None

    def start(self):
        self.__timer = Timer(self.__interval, self.__loop)
        self.__timer.start()

    def stop(self):
        self.__timer.cancel()

    def __loop(self):
        self.log_it(self._progress_summary())
        self.start()

    def _progress_summary(self):
        raise NotImplementedError()

    def log_it(self, message):
        self.__output.write("## (%s) -- %s\n" % (current_timestamp(), message))


class IteratorLogger(Logger):
    def __init__(self, iterator, *args):
        super(IteratorLogger, self).__init__(*args)
        self._iterator = iterator

    def _progress_summary(self):
        return self._iterator.info()