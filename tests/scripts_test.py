from nose.tools import *
from __main__.__main__.scripts import Script

class ScriptStub(Script):
    def _setup(self):
        self._add_option("-v", "--val", dest="value", default=1)

    def getVal(self):
        return self._get_option('value')

    def getArg(self):
        return self._get_arg(0)

    def _run_script(self):
        self.run = True

class TestScript:
    def setup(self):
        self.script = ScriptStub()

    def test_argument_processing(self):
        self.script.execute(['-v', '10', '20'])
        assert '10' == self.script.getVal()
        assert '20' == self.script.getArg()

    def test_run_method_called(self):
        self.script.execute()
        assert True == self.script.run

    @raises(NotImplementedError)
    def test_raises_error_on_father(self):
        Script()