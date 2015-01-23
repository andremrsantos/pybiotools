from __main__.__main__.scripts import FileScript
from __main__.__main__.helpers import io_helper


class FileScriptStub(FileScript):
    def _setup(self):
        super(FileScriptStub, self)._setup()
        self._ct = 0

    def _process(self, line):
        print line.rstrip()
        self._ct += 1

    def getCt(self):
        return self._ct

def test_file_iterator():
    stub = FileScriptStub()
    stub.execute(['-i', 'LICENSE'])
    assert io_helper.line_number('LICENSE') == stub.getCt()
