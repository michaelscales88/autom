from os.path import dirname, join, isfile, abspath
from os import getcwd
from datetime import timedelta, datetime, time, date
from dateutil.parser import parse

from automated_sla_tool.src.report_templates import ReportTemplate
from automated_sla_tool.src.report_utilities import ReportUtilities
from automated_sla_tool.src.final_report import FinalReport
from automated_sla_tool.src.app_settings import AppSettings
from automated_sla_tool.src.data_center import DataCenter


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)


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

        # self.active_directory = r'{0}\{1}'.format(self.path, r'active_files')
        # self.converter_arg = r'{0}\{1}'.format(self.path, r'converter\ofc.ini')
        # self.converter_exc = r'{0}\{1}'.format(self.path, r'converter\ofc.exe')
        # self.login_type = r'imap.gmail.com'
        # self.user_name = r'mindwirelessreporting@gmail.com'
        # self.password = r'7b!2gX4bD3'

        if isinstance(self._inr, date):
            self.util_datetime = datetime.combine(self._inr, time())
            self.day_of_wk = self._inr.weekday()
            self.src_doc_path = self.open_src_dir()
        else:
            self.util_datetime = None
            self.day_of_wk = None

    @property
    def date(self):
        return self.output.date

    @property
    def type(self):
        return self.output.type

    @property
    def save_path(self):
        return self.output.save_path

    # TODO abstract this -> *args
    # TODO 2: error handling for BadZipFile error from openpyxl. handles corrupted files
    # TODO 3: Move this into ReportUtilities. Keep filter_chronicall_reports in this class
    # TODO 4: Error handling should prompt the user to redownload the file
    def load(self):
        if self._output.finished:
            return
        else:
            for f_name, file in self.util.load_data(self):
                # print(f_name)
                # print(type(f_name))
                # print(type(file))
                self.src_files[f_name] = file
            # raise SystemExit()
            # for (f, p) in self.loader(self.req_src_files).items():
            #     try:
            #         file = self.context_manager(p)
            #         self.src_files[f] = self.filter_chronicall_reports(file)
            #     except (IndexError, TypeError):
            #         print(self.src_files.keys())
            #         print('I hit an issue opening my src file: {file}.\n'
            #               'Please try to open and re-save before proceeding.'.format(file=f))
            #         self.util.open_directory(self.src_doc_path)
            #         file = self.context_manager(p)
            #         self.src_files[f] = self.filter_chronicall_reports(file)
            #     except KeyError:
            #         self.util.open_directory(self.src_doc_path)

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

    # # TODO push this into ReportUtilities
    # def clean_src_loc(self, spc_ch, del_ch):
    #     Ex. Call  self.clean_src_loc(spc_ch=['-', '_'],
    #                        del_ch=['%', r'\d+'])
    #     # TODO today test this more... doesn't merge/delete original file
    #     file_list = [f for f in listdir(self.src_doc_path) if f.endswith((".xlsx", ".xls"))]
    #     for f in file_list:
    #         f_name, ext = splitext(f)
    #         f_name = sub('[{spc_chrs}]'.format(spc_chrs=''.join(spc_ch)), ' ', f_name)
    #         f_name = sub('[{del_chs}]'.format(del_chs=''.join(del_ch)), '', f_name)
    #         f_name = f_name.strip()
    #         old_f = join(self.src_doc_path, f)
    #         new_f = join(self.src_doc_path, r'{f_name}{ext}'.format(f_name=f_name,
    #                                                                 ext=ext))
    #         rename(old_f, new_f)

    def print_output(self):
        print(self.output)

    def chck_rpt_dates(self, sheet):
        first = self.chck_w_in_days(sheet.column['Start Time'][0])
        try:
            last = self.chck_w_in_days(sheet.column['End Time'][-1])
        except ValueError:
            last = False
        if first or last:
            pass
        else:
            raise ValueError

    # General Utilities
    def chck_w_in_days(self, doc_dt, num_days=1):
        try:
            date_time = parse(doc_dt)
        except ValueError:
            return False
        else:
            if (date_time - self.util_datetime) <= timedelta(days=num_days):
                return True
            else:
                return False

    # def download_chronicall_files(self, file_list):
    #     '''
    #     Temporary
    #     self.login_type = r'imap.gmail.com'
    #     self.user_name = r'mindwirelessreporting@gmail.com'
    #     self.password = r'7b!2gX4bD3'
    #     '''
    #     import email
    #     import imaplib
    #     if file_list not in listdir(self.src_doc_path):
    #         try:
    #             imap_session = imaplib.IMAP4_SSL(self.login_type)
    #             status, account_details = imap_session.login(self.user_name, self.password)
    #             if status != 'OK':
    #                 raise ValueError('Not able to sign in!')
    #
    #             imap_session.select("Inbox")
    #             on = "ON " + (self._inr + timedelta(days=1)).strftime("%d-%b-%Y")
    #             status, data = imap_session.uid('search', on, 'FROM "Chronicall Reports"')
    #             if status != 'OK':
    #                 raise ValueError('Error searching Inbox.')
    #
    #             # Iterating over all emails
    #             for msg_id in data[0].split():
    #                 status, message_parts = imap_session.uid('fetch', msg_id, '(RFC822)')
    #                 if status != 'OK':
    #                     raise ValueError('Error fetching mail.')
    #
    #                 mail = email.message_from_bytes(message_parts[0][1])
    #                 for part in mail.walk():
    #                     if part.get_content_maintype() == 'multipart':
    #                         continue
    #                     if part.get('Content-Disposition') is None:
    #                         continue
    #                     file_name = part.get_filename()
    #
    #                     if bool(file_name):
    #                         file_path = join(self.src_doc_path, file_name)
    #                         if not isfile(file_path):
    #                             fp = open(file_path, 'wb')
    #                             fp.write(part.get_payload(decode=True))
    #                             fp.close()
    #
    #             imap_session.close()
    #             imap_session.logout()
    #
    #         except Exception as err:
    #             raise ValueError('Not able to download all attachments. Error: {}'.format(err))
    #     else:
    #         print("Files already downloaded.")

    # TODO these can be removed once MarsReport is refactored to crawl reports SlaReport E.g. for row and col in rpt
    def correlate_list_time_data(self, src_list, list_to_correlate, key):
        return_list = []
        for event in self.util.find(src_list, key):
            return_list.append(self.util.get_sec(list_to_correlate[event]))
        return return_list

    def correlate_list_val_data(self, src_list, list_to_correlate, key):
        return_list = []
        for event in self.util.find(src_list, key):
            return_list.append(list_to_correlate[event])
        return return_list

    def transmit_report(self):
        return self._output

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

    def safe_parse_dt(self, dt_time=None, default_date=None, default_rtn=None):
        try:
            return parse(dt_time, default=(default_date if default_date else self.util_datetime))
        except ValueError:
            return default_rtn if default_rtn is not None else self.util_datetime

    def parse_to_sec(self, dt=None):
        dt_t = self.util.safe_parse(dt).time()
        return self.util.convert_sec(h=dt_t.hour, m=dt_t.minute, s=dt_t.second)

    def read_time(self, time_object, spc_chr='*'):
        try:
            return_time = time_object.split(spc_chr)[0]
        except AttributeError:
            try:
                return_time = time_object.time()
            except AttributeError:
                return_time = time_object
        else:
            return_time = self.safe_parse_dt(return_time).time()
        return return_time
