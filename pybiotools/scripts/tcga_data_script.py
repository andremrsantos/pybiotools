from file_script import FileScript, FileIterator
from os import path, getcwd, makedirs

class TCGADataScript(FileScript):
    def _setup(self):
        super(TCGADataScript, self)._setup()
        self._add_option('-c', '--cancer-group', dest='cancer',
                         help='TCGA cancer label to be downloaded')
        self._add_option('-g', '--group-table', dest='group_table',
                         help='Group available data table')

    def _init_process(self):
        super(TCGADataScript, self)._init_process()
        self.__set_folder()

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

        iterator = FileIterator(self._get_option('group_table'))
        while iterator.has_next():
            arr = iterator.next().split()
            if arr[0] == self._get_option('cancer'):
                self.__profile.append(arr[1])
                self.__cases.append(arr[0])

    def _process(self, line):
        pass

