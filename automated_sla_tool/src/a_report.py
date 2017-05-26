from os.path import dirname, join, isfile


from automated_sla_tool.src.report_templates import ReportTemplate
from automated_sla_tool.src.report_utilities import ReportUtilities
from automated_sla_tool.src.final_report import FinalReport
from automated_sla_tool.src.app_settings import AppSettings
from automated_sla_tool.src.data_center import DataCenter


class AReport(ReportTemplate):
    def __init__(self, rpt_inr=None, test_mode=False):
        super().__init__()
        self.test_mode = test_mode
        self.data_center = DataCenter()
        self.util = ReportUtilities()
        self.interval = rpt_inr if rpt_inr else self.manual_input()
        self.settings = AppSettings(app=self)
        self.output = FinalReport(report_type=self.settings['report_type'],
                                  report_date=self._inr,
                                  my_report=self)
        self.req_src_files = self.settings.setting('req_src_files', rtn_val=[])
        self.src_doc_path = self.open_src_dir()

    @property
    def date(self):
        return self.output.date

    @property
    def type(self):
        return self.output.type

    @property
    def save_path(self):
        return self.output.save_path

    def load(self):
        if self._output.finished:
            return
        else:
            for f_name, file in self.util.load_data(self):
                self.src_files[f_name] = file

            if self.req_src_files:
                print('Could not find files:\n{files}'.format(
                    files='\n'.join([f for f in self.req_src_files])
                ), flush=True)
                raise SystemExit()

    def open(self):
        self.data_center.dispatcher(self)

    def save(self):
        if not self.test_mode:
            for save_name, save_location in self.settings['Save Targets'].items():
                print('Saving', save_name)
                self.data_center.save(
                    file=self.output,
                    full_path=save_location
                )
                print('Successfully saved', save_name)

    def __del__(self):
        if not self.test_mode:
            self.open()

    def open_src_dir(self):
        file_dir = r'{dir}\{sub}\{yr}\{tgt}'.format(dir=dirname(self.path),
                                                    sub='Attachment Archive',
                                                    yr=self.interval.strftime('%Y'),
                                                    tgt=self.interval.strftime('%m%d'))
        self.util.make_dir(file_dir)
        return file_dir

    def check_finished(self, report_string=None, sub_dir=None, fmt='xlsx'):
        if report_string and sub_dir:
            the_file = join(self._output.save_path, sub_dir, '{file}.{ext}'.format(file=report_string, ext=fmt))
            if isfile(the_file):
                print('I know this file is completed.')
                self._output.open_existing(the_file)
            return self._output.finished
        else:
            print('No report_string in check_finished'
                  '-> Cannot check if file is completed.')
