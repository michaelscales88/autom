from os.path import dirname, abspath


class ReportTemplate(object):
    def __init__(self):
        self._path = dirname(dirname(abspath(__file__)))
        self._name = None
        self._ext = None
        self.src_files = {}
        self._inr = None
        self._util = None
        self._inr = None
        self._settings = None
        self._output = None
        self.req_src_files = None

    @property
    def path(self):
        return self._path

    @property
    def interval(self):
        return self._inr

    @interval.setter
    def interval(self, new_interval):
        if not self._inr:
            self._inr = new_interval

    @property
    def util(self):
        return self._util

    @util.setter
    def util(self, new_util):
        if not self._util:
            self._util = new_util

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new_settings):
        if not self._settings:
            self._settings = new_settings

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, new_output):
        if not self._output:
            self._output = new_output

    def manual_input(self):
        pass

    def load(self):
        pass

    def run(self):
        pass

    def open(self):
        pass

    def save(self):
        pass
