from optparse import OptionParser


class Script(object):
    def __init__(self, *args):
        self.__parser = OptionParser()
        self._setup()

    def _setup(self):
        raise NotImplementedError()

    def _add_option(self, *args, **kw):
        self.__parser.add_option(*args, **kw)

    def _get_option(self, key):
        return self.__options.__dict__[key]

    def _get_arg(self, index):
        return self.__args[index]

    def execute(self, args=[]):
        (self.__options, self.__args) = self.__parser.parse_args(args)
        self._run_script()

    def _run_script(self):
        raise NotImplementedError()

    def _name(self):
        return self.__class__.__name__