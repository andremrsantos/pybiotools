from csv import DictWriter, QUOTE_NONNUMERIC

from pybiotools.helpers.collection_helpers import unique
from pybiotools.helpers.io_helper import line_number
from pybiotools.crawlers.cbio_crawler import CBioCrawler
from pybiotools.iterators import CSVIterator
from file_script import FileScript
from os import path, getcwd, makedirs


class TCGADataScript(FileScript):
    Iterator = CSVIterator

    def _setup(self):
        super(TCGADataScript, self)._setup()
        self._add_option('-c', '--cancer-group', dest='cancer',
                         help='TCGA cancer label to be downloaded')
        self._add_option('-g', '--group-table', dest='group_table',
                         help='Group available data table')

    def _init_process(self):
        super(TCGADataScript, self)._init_process()
        self.__set_folder()
        self.__load_group()
        self.__crawler = CBioCrawler()
        self.__crawler.set_cases(self.__cases)
        self.__crawler.set_profiles(self.__profile)

    def __set_folder(self):
        self.__output_folder = path.join(getcwd(), self._get_option('cancer'))
        if not path.exists(self.__output_folder) :
            self._logger.log_it('Creating folder %s' % self.__output_folder)
            makedirs(self.__output_folder)
        if not path.isdir(self.__output_folder):
            raise IOError()

    def __load_group(self):
        self.__profile = []
        self.__cases = []

        iterator = CSVIterator(self._get_option('group_table'))
        while iterator.has_next():
            (_c, _profile, _case) = iterator.next()
            if _c == self._get_option('cancer'):
                self.__profile.append(_profile)
                self.__cases.append(_case)

        self.__profile = unique(self.__profile)
        self.__cases = unique(self.__cases)

    def _process(self, set):
        (ezid, eff, symbol) = set
        opath = path.join(self.__output_folder,
                          "{id:}.{sym:}.csv".format(id=ezid, sym=symbol))

        if path.exists(opath) and line_number(opath) >= len(self.__profile):
            self.__crawler.set_genes(ezid)
            try:
                tcga = TCGAData(self.__crawler.get_profile_data())
                tcga.set('geneid', ezid)
                tcga.set('snpEff', eff)
                tcga.set('hgcBio', symbol)
                tcga.write(opath)
            except Exception, e:
                self._logger.log_it("[ERROR] Unable to process gene")
                self._logger.log_it(e.message)


class TCGAData(object):
    def __init__(self, data, delimiter="\t"):
        self.__raw_data = data.splitlines()
        self.__delimiter = delimiter
        self.__keys = self.__raw_data.pop(0).rstrip().rsplit(self.__delimiter)
        self.__samples = [i for i in self.__keys if i.startswith('TCGA')]
        self.__fields = ['']
        self.__process()

    def set(self, key, value):
        for entry in self.__data:
            entry[key] = value

    def write(self, opath):
        writer = DictWriter(open(opath, 'w'), fields=self.__fields,
                            delimiter=self.__delimiter,
                            quoting=QUOTE_NONNUMERIC)
        for entry in self.__data:
            writer.writerow(entry)

    def __to_dict(self, line):
        dic = {}
        arr = line.rstrip().rsplit(self.__delimiter)
        for i in xrange(0, len(self.__keys)):
            dic[self.__keys[i]] = arr[i]
        return dic

    def __process(self):
        data = {}
        for line in self.__raw_data:
            dic = self.__to_dict(line)
            if dic['GENETIC_PROFILE_ID'] not in self.__fields:
                self.__fields.append(dic['GENETIC_PROFILE_ID'])

            for sample in self.__samples:
                sample_data = {'': sample, dic['GENETIC_PROFILE_ID']: dic[sample]}
                if sample in data:
                    data[sample].update(sample_data)
                else:
                    data[sample] = sample_data
        self.__data = data.values()