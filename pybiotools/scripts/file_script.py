from pybiotools.helpers.loggers import IteratorLogger
from pybiotools.iterators import FileIterator
from script import Script
from re import match


class FileScript(Script):
    Iterator = FileIterator
    Logger = IteratorLogger

    def _setup(self):
        self._add_option('-i', '--input', dest='fname',
                         help='Reading input file')

    def _run_script(self):
        self._iterator = self.__class__.Iterator(self._get_option('fname'))
        self._logger = self.__class__.Logger(self._iterator)
        self._logger.log_it("Init %s processing..." % self._name())

        self._logger.start()
        while self._iterator.has_next():
            line = self._iterator.next()
            if match(r'^(#|$)', line):
                continue
            self._process(line)

        self._logger.stop()
        self._logger.log_it("Completed %s Execution" % self._name())

    def _process(self, line):
        raise NotImplementedError