from collections import OrderedDict
from json import dumps
from datetime import datetime


from automated_sla_tool.src.fn_lib import FnLib
from automated_sla_tool.src.report_utilities import ReportUtilities


class DataWorker(object):

    def __init__(self, target=None):
        self._commands = {}
        self.fn_lib = FnLib()
        self.commands(target)
        self.current_target = target

    @staticmethod
    def my_business(obj):
        try:
            return obj.settings['JSON'].items()
        except AttributeError:
            return ()

    @staticmethod
    def bind_keyword(keywords, bindings):
        return dict(zip(keywords.split(':'), bindings.split(':')))

    def commands(self, obj):
        try:
            parsed_commands = self._commands[obj.__module__]    # unsure why this works, but .get doesn't
        except KeyError:
            parsed_commands = {
                key: self._link(*values) for key, values in DataWorker.my_business(obj)
            }
        # parsed_commands = self._commands.get(
        #     obj.__module__,
        #     {
        #         key: self._link(*values) for key, values in DataWorker.my_business(obj)
        #     }
        # )
        # print(parsed_commands)
        self._commands[obj.__module__] = parsed_commands
        for row, cmds in parsed_commands.items():
            yield row, cmds

    # This could be a way for datworker to make reports
    def execute(self, obj):
        for row, cmds in self.commands(obj):
            pass

    # TODO add a way to bind fn to behavior or parameters
    def _link(self, *words):
        fn = self.fn_lib[words[0]]
        parameters = DataWorker.bind_keyword(words[1], words[2])
        # print('Inside _link', datetime.today().time(), flush=True)
        # print([word for word in words[3:]])
        behaviors = tuple(self.fn_lib[word] for word in words[3:])
        return {'fn': fn, 'parameters': parameters, 'behaviors': behaviors}

    def __iter__(self):
        for row, cmds in self.commands(self.current_target):
            yield row, cmds
