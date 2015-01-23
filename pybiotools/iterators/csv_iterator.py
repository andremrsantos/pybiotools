from file_iterator import FileIterator
from csv import reader, Sniffer


class CSVIterator(FileIterator):
    def __init__(self, fname, delimiter="\t"):
        super(CSVIterator, self).__init__(fname)
        dialect = Sniffer().sniff(self._finput.read(1024))
        self._finput.seek(0)
        self._reader = reader(self._finput, delimiter=delimiter,
                              dialect=dialect)

    def next(self):
        self._advance()
        return self._reader.next()