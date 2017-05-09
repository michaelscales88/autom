import inspect
import traceback
from time import sleep

from automated_sla_tool.src.finished_decorator import FinishedDecorator as check_set
from automated_sla_tool.src.stacked_traceback_decorator import StackedTracebackDecorator as tb_decorator
from automated_sla_tool.src.timeit import timeit


class GenericUi(object):
    obj_set = False

    @check_set(obj_set)
    def __init__(self, exclusions=None):
        super().__init__()
        self._finished = False
        self._obj = None
        self._ui = None
        self._safe = False
        self._exclusions = ['__init__', exclusions]

    def run(self):
        while not self.finished:
            try:
                self.display_ui()
            except AttributeError:
                return
            except Exception:
                sleep(.5)
                print(traceback.format_exc())

    @property
    def finished(self):
        return self._finished

    @property
    def object(self):
        return self._obj

    @object.setter
    @check_set(obj_set)
    def object(self, raw_obj):
        obj = raw_obj
        obj_ui = {
            **dict(inspect.getmembers(obj, predicate=inspect.ismethod)),
            **{'Quit': self.exit,
               'Setmode Safe': self.toggle_safe_mode,
               'Time It': self.time_fn
               }
        }
        for e in self._exclusions:
            obj_ui.pop(e, None)
        self._obj = obj
        self._ui = obj_ui
        GenericUi.obj_set = True

    def clear_obj(self):
        self._obj = None
        self._ui = None
        GenericUi.obj_set = False

    def display_ui(self):
        return self.exc_fnc_safe_mode() if self._safe else self.exc_fnc()

    def exc_fnc(self):
        selection = dict(enumerate(sorted(self._ui.keys()), start=1))
        self.display_selection(selection)
        func = self._ui[selection[int(input('Make a selection: '))]]
        return func()

    def toggle_safe_mode(self):
        self._safe = not self._safe

    def exit(self):
        self._finished = True

    @tb_decorator()
    def exc_fnc_safe_mode(self):
        return self.exc_fnc()

    @timeit
    def time_fn(self):
        print('Performing timeit on next menu selection:')
        return self.exc_fnc()

    def display_selection(self, selection):
        print('GenericUI: {app}\n'
              'Safe Mode: {mode}'.format(app=self._obj.__class__.__name__,
                                         mode=('Not Active', 'Safe Active')[self._safe]), flush=True)
        print("\n".join(['{k}: {v}'.format(k=k, v=v) for k, v in sorted(selection.items())]))

    def __del__(self):
        print('Exiting GenericUI: {app}'.format(app=self._obj.__class__.__name__))
