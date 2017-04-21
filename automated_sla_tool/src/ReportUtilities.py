from datetime import datetime, date, time, timedelta
from os import listdir, rename, startfile
from dateutil.parser import parse
from pyexcel import Book, Sheet, get_book
from subprocess import Popen
from re import split, sub
from os.path import join, splitext, basename
from pywinauto.findwindows import find_window, WindowNotFoundError
from pywinauto.controls.hwndwrapper import HwndWrapper

from automated_sla_tool.src.UtilityObject import UtilityObject
from automated_sla_tool.src.factory import get_loader


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)


class BoundSettings(object):
    def __init__(self):
        self._bound_settings = []
        self._cwd = None

    @property
    def current_binding(self):
        return self._bound_settings

    @current_binding.setter
    def current_binding(self, new_binding):
        self._bound_settings = new_binding

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, new_dir):
        self._cwd = new_dir


class ReportUtilities(UtilityObject):
    def __init__(self):
        super().__init__()
        self._bound_settings = BoundSettings()
        self._bound_connection = None

    @property
    def cwd(self):
        return self._bound_settings.cwd

    @cwd.setter
    def cwd(self, new_wd):
        self._bound_settings.cwd = new_wd

    @property
    def bind_settings(self):
        return tuple(self._bound_settings.current_binding)

    @bind_settings.setter
    def bind_settings(self, new_binding):
        self._bound_settings.current_binding = new_binding

    @property
    def bind_connection(self):
        return self._bound_connection

    @bind_connection.setter
    def bind_connection(self, new_binding):
        self._bound_connection = new_binding

    @staticmethod
    def is_weekday(given_day):
        try:
            return ReportUtilities.day_of_week(given_day) not in (5, 6)
        except AttributeError:
            print('{date} is invalid to get day of the week.'.format(date=given_day))

    @staticmethod
    def day_of_week(given_day):
        return given_day.weekday() if isinstance(given_day, (datetime, date)) else 'Unknown Date'

    @staticmethod
    def name_of_day(given_day):
        return given_day.strftime('%A') if isinstance(given_day, (datetime, date)) else 'Unknown Date'

    @staticmethod
    def date_to_dt(raw_date):
        return datetime.combine(raw_date, time()) if isinstance(raw_date, date) else raw_date

    @staticmethod
    def phone_number(mixed_string):
        only_digits = [ch for ch in str(mixed_string) if ch.isdigit()]
        try:
            return int(
                str(
                    ''.join(
                        only_digits[1:]
                        if len(only_digits) > 7 and only_digits[0] == 1
                        else only_digits
                    )
                )
            )
        except ValueError:
            return None

    @staticmethod
    def find_non_distinct(sheet=None, event_col=None):
        i_count = {}
        for row_name in reversed(sheet.rownames):
            dup_event = sheet[row_name, event_col]
            dup_info = i_count.get(
                dup_event, {
                    'count': 0,
                    'rows': []
                }
            )
            dup_info['count'] += 1
            dup_info['rows'].append(row_name)
            i_count[dup_event] = dup_info
        return i_count

    @staticmethod
    def datetime_handler(x):
        # print(type(x))
        if isinstance(x, datetime):
            return x.isoformat()
        elif isinstance(x, timedelta):
            return str(x)
        else:
            return str(x)
        # raise TypeError("Unknown type")

    @staticmethod
    def apply_format_to_wb(wb, filters=(), one_filter=None):
        for sheet in wb:
            ReportUtilities.apply_format_to_sheet(sheet, filters, one_filter)

    @staticmethod
    def to_td(v):
        try:
            v = timedelta(seconds=ReportUtilities.get_sec(v))
        except (AttributeError, ValueError) as e:
            print(e, v)
        return v

    @staticmethod
    def to_dt(v):
        try:
            v = parse(v)
        except (AttributeError, ValueError) as e:
            print(e, v)
        return v

    @staticmethod
    def apply_format_to_sheet(sheet, filters=(), one_filter=None):
        for a_filter in filters:
            del sheet.row[a_filter]
        if one_filter:
            del sheet.row[one_filter]

    @staticmethod
    def collate_wb_to_sheet(wb=()):
        headers = ['row_names'] + wb[0].colnames
        sheet_to_replace_wb = Sheet(colnames=headers)
        unique_records = UniqueDict()
        for sheet in wb:
            for i, name in enumerate(sheet.rownames):
                unique_records[name] = sheet.row_at(i)
        for rec in sorted(unique_records.keys()):
            sheet_to_replace_wb.row += [rec] + unique_records[rec]
        sheet_to_replace_wb.name_rows_by_column(0)
        return sheet_to_replace_wb

    @staticmethod
    def shortest_longest(*args):
        return (args[0], args[1]) if args[0] is min(*args, key=len) else (args[1], args[0])

    @staticmethod
    def return_selection(input_opt):
        selection = list(input_opt.values())
        return selection[
            int(
                input(
                    ''.join(['{k}: {i}\n'.format(k=k, i=i) for i, k in enumerate(input_opt)])
                )
            )
        ]

    @staticmethod
    def find(lst, a):
        return [i for i, x in enumerate(lst) if x == a]

    @staticmethod
    def is_empty_wb(book):
        if isinstance(book, Book):
            return book.number_of_sheets() is 0

    @staticmethod
    def make_summary(headers):
        todays_summary = Sheet()
        todays_summary.row += headers
        todays_summary.name_columns_by_row(0)
        return todays_summary

    # TODO consider methods like this to move into UtilityObject
    @staticmethod
    def add_time(dt_t, add_time=None):
        return (datetime.combine(datetime.today(), dt_t) + add_time).time()

    @staticmethod
    def safe_parse(dt=None):
        try:
            return parse(dt)
        except ValueError:
            print('Could not parse date_time: {dt}'.format(dt=dt))

    # TODO beef this up to handle multiple kinds of files
    # TODO create a dict with functions mapped to the ext
    @staticmethod
    def context_manager(file_name, ext):
        print('Opening', file_name)
        with open(file_name, mode='rb') as file_object:
            file_content = file_object.read()
            return get_book(file_content=file_content, file_type=ext)

    def clean_dir(self):
        # Should get spc characters and del characters from settings
        pass
        # file_list = [f for f in listdir(self.connection.src_doc_path) if f.endswith((".xlsx", ".xls"))]
        # for f in file_list:
        #     f_name, ext = splitext(f)
        #     f_name = sub('[{spc_chrs}]'.format(spc_chrs=''.join(spc_ch)), ' ', f_name)
        #     f_name = sub('[{del_chs}]'.format(del_chs=''.join(del_ch)), '', f_name)
        #     f_name = f_name.strip()
        #     old_f = join(self.src_doc_path, f)
        #     new_f = join(self.src_doc_path, r'{f_name}{ext}'.format(f_name=f_name,
        #                                                             ext=ext))
        #     rename(old_f, new_f)

    @staticmethod
    def prepare_excel(file):
        ReportUtilities.remove_sheets_per_settings(file)
        for sheet_name in reversed(file.sheet_names()):
            sheet = file.sheet_by_name(sheet_name)
            ReportUtilities.apply_header_filters(sheet)
            ReportUtilities.apply_body_filters(sheet)

    @staticmethod
    def apply_header_filters(work_sheet):
        del work_sheet.row[ReportUtilities.header_filter]
        work_sheet.name_rows_by_column(0)
        work_sheet.name_columns_by_row(0)

    @staticmethod
    def apply_body_filters(work_sheet):
        # workbook.remove_sheet('Summary') -> map this to settings
        # try:
        #     self.chck_rpt_dates(sheet)
        # except ValueError:
        #     workbook.remove_sheet(sheet_name)
        pass

    @staticmethod
    def remove_sheets_per_settings(workbook):
        workbook.remove_sheet('Summary')
        # for sheet_to_remove in ['Summary']:
        #     try:
        #         workbook.remove_sheet(sheet_to_remove)
        #     except KeyError:
        #         pass

    # TODO this need to be able to handle more data types than excel
    # TODO 2: this should also download files
    @staticmethod
    def load_data(report):
        print('testing load_data')

        ld = get_loader()
        ld.connection = report
        ld.cwd = report.src_doc_path

        # self.bind_settings = report.settings['Header Formats']

        for f_name, path, ext in ld.load_or_dl(report.req_src_files):
            print(f_name, path)
            try:
                file = ReportUtilities.context_manager(path, ext)
                ReportUtilities.prepare_excel(file)
            except (IndexError, TypeError) as e:
                print(e)
                print('Encountered an issue with file: {file_name}\n'
                      'Try to open and save the file.'.format(file_name=f_name))
                ReportUtilities.open_directory(report.src_doc_path)

                file = ReportUtilities.context_manager(path, ext)
                ReportUtilities.prepare_excel(file)
            yield f_name, file

        # self.bind_settings = []
        print('test complete')

    @staticmethod
    def safe_div(num, denom):
        rtn_val = 0
        try:
            rtn_val = num / denom
        except ZeroDivisionError:
            pass
        return rtn_val

    # Generator Section
    @staticmethod
    def common_keys(*dcts):
        for i in set(dcts[0]).intersection(*dcts[1:]):
            yield (i,) + tuple(d[i] for d in dcts)

    @staticmethod
    def return_matches(*args, match_val=None):
        if len(args) == 2:
            shortest_list, longest_list = ReportUtilities.shortest_longest(*args)
            print(shortest_list)
            print(longest_list)
            longest_list_indexed = {}
            for item in longest_list:
                longest_list_indexed[item[match_val]] = item
            for item in shortest_list:
                if item[match_val] in longest_list_indexed:
                    print('matches thinks i found a match')
                    yield item, longest_list_indexed[item[match_val]]

    # Filter Section
    @staticmethod
    def header_filter(row_index, row):
        corner_case = split('\(| - ', row[0])
        bad_word = corner_case[0].split(' ')[0] not in ('Feature', 'Call', 'Event')
        # bad_word = corner_case[0].split(' ')[0] not in tuple(ReportUtilities.bound_settings)
        # bad_words = ReportUtilities.bound_settings
        return True if len(corner_case) > 1 else bad_word

    @staticmethod
    def blank_row_filter(row_index, row):
        result = [element for element in str(row[3]) if element != '']
        return len(result) == 0

    @staticmethod
    def answered_filter(row_index, row):
        try:
            answered = row[-5]
        except ValueError:
            answered = False
        return answered

    @staticmethod
    def inbound_call_filter(row_index, row):
        return row[0] not in ('Inbound', 'Call Direction')

    @staticmethod
    def zero_duration_filter(row_index, row):
        result = [element for element in row[-1] if element != '']
        return len(result) == 0

    @staticmethod
    def remove_internal_inbound_filter(row_index, row):
        return row[-2] == row[-3]

    @staticmethod
    def open_focus(target, p_type='explorer'):
        try:
            HwndWrapper(find_window(title=ReportUtilities.base(target))).set_focus()
        except WindowNotFoundError:
            Popen('{process} "{path}"'.format(
                process=p_type,
                path=target)
            )
        except FileNotFoundError:
            print('File: {target} does not exist.'.format(target=target))

    @staticmethod
    def open_directory(tgt_dir):
        ReportUtilities.open_focus(tgt_dir)
        input('Any key to continue.')

    # TODO this is actually confusing as hell. need to update this to be more programmatic
    # @staticmethod
    # def full_path(base_path=None, report=None):
    #     folder_path = ReportUtilities.resolve_path(
    #         report=report,
    #         tgt_path=base_path
    #     )
    #     file_name = ReportUtilities.resolve_name(
    #         report=report,
    #         file_name=ReportUtilities.base(base_path)
    #     )
    #     return join(folder_path, file_name)

    @staticmethod
    def start(full_path):
        ReportUtilities.open_focus(full_path)

    # @staticmethod
    # def resolve_name(report=None, file_name=None, f_ext='xlsx'):
    #     try:
    #         file_string = ReportUtilities.compare_two(
    #             (file_name, file_name),
    #             (hasattr(report, 'settings'), report.settings['file_fmt'])
    #         )
    #         # if str_fmt:
    #         #     file_string = str_fmt.format(date=report.date.strftime("%m%d%Y"))
    #         # else:
    #         #     file_string = '{date}_{type}'.format(date=report.date, type=report.type)
    #         if file_string is None:
    #             print('raising value')
    #             raise ValueError()
    #     except ValueError:
    #         print("Couldn't find a name\n"
    #               "to save file")
    #     except AttributeError:
    #         print('ReportUtilities.resolve_name: \n'
    #               'Check report is correct type')
    #     else:
    #         print('exiting as expected')
    #         return '{f_string}.{fmt}'.format(f_string=file_string,
    #                                          fmt=f_ext)
    #
    # # TODO probably need to merge  tgt_path and sub_dir for simplicity
    # @staticmethod
    # def resolve_path(report=None, tgt_path=None, sub_dir=None):
    #     try:
    #         tgt_path = ReportUtilities.compare_two(
    #             (tgt_path, tgt_path),
    #             (hasattr(report, 'save_path'), report.save_path)
    #         )
    #         if tgt_path and sub_dir:
    #             path = join(tgt_path, sub_dir)
    #         elif tgt_path and hasattr(report, 'settings'):
    #             path = join(tgt_path, report.settings['sub_dir_fmt'])
    #         else:
    #             raise ValueError()
    #     except ValueError:
    #         print('No location provided '
    #               'to save file: {name} {type}'.format(name=report.date,
    #                                                    type=report.type))
    #     except AttributeError:
    #         print('ReportUtilities.resolve_path: \n'
    #               'Check report is correct type')
    #     else:
    #         return path

