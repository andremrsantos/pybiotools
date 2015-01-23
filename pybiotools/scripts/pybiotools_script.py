from pybiotools.scripts import Script, TCGADataScript


class PyBiotoolsScript(Script):
    SCRIPTS = [TCGADataScript]

    def _setup(self):
        self.__scripts = {}
        for script in self.__class__.SCRIPTS:
            self.__scripts[script.name()] = script

    def _run_script(self):
        args = self._args()
        script_name = args.pop(0)
        if self.__scripts not in script_name:
            raise AttributeError("Script '%s' unavailable" % script_name)
        self.__scripts[script_name]().execute(args)

    @classmethod
    def _usage(cls):
        scripts_name = [i.name() for i in cls.SCRIPTS]
        return "__main__.py <ScriptName> [options] [args]\n" \
               "Scripts Available:\n%s" % "\n".join(scripts_name)