import pyexcel as pe
from os.path import dirname, join
from datetime import date


# TODO this might be better as an object with a sheet ->
# TODO to handle name conflict with nominable Sheet and prop sheet
class FinalReport(pe.Sheet):

    def __init__(self, **kwargs):
        self._data = {
            'type': kwargs.get('report_type', None),
            'date': kwargs.get('report_date', None),
            'my_report': kwargs.get('my_report', None),
        }
        report_name = (
            self._data['date'].strftime("%m-%d-%Y") if isinstance(self._data['date'], date) else self._data['date']
        )
        super().__init__(name=report_name, **kwargs)
        self._finished = False
        self._table_set = False

    '''
    Properties
    '''

    @property
    def save_path(self):
        return r'{dir}\Output\{sub_dir}'.format(dir=dirname(self.report.path),
                                                sub_dir=self.type)

    @property
    def rpt_name(self):
        return '{d}_{t}'.format(d=self._data['date'].strftime("%m%d%Y"),
                                t=self._data['type'])

    @property
    def report(self):
        return self._data['my_report']

    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, is_fin):
        self._finished = is_fin

    @property
    def type(self):
        return self._data['type']

    @property
    def date(self):
        return self._data['date']

    '''
    OS Operations
    '''

    def open_report(self, the_file):
        if not self.finished:
            sheet = pe.get_sheet(file_name=the_file)
            for row in sheet.rows():
                self.row += row
            self.name_columns_by_row(0)
            self.name_rows_by_column(0)
            self._finished = True

    def save(self, str_fmt=None, save_format='xlsx', tgt_path=None, sub_dir=None, full_path=None):
        if full_path:
            self.save_as(filename=full_path)
        else:
            try:
                file_string = str_fmt if str_fmt else '{date}_{type}'.format(date=self.date,
                                                                             type=self.type)
                file_name = '{f_string}.{fmt}'.format(f_string=file_string,
                                                      fmt=save_format)
                if tgt_path and sub_dir:
                    path = join(tgt_path, sub_dir)
                elif sub_dir:
                    path = join(self.save_path, sub_dir)
                else:
                    raise ValueError()
            except ValueError:
                print('No location provided'
                      'to save file: {name} {type}'.format(name=self.date,
                                                           type=self.type))
            else:
                self.save_as(filename=join(path, file_name))

    '''
    Report Section
    '''

    def format_columns_with(self, f, *columns):  # w/ named rows and columns
        for column in columns:
            for col_name in self.colnames:
                if column in col_name:
                    for row_name in self.rownames:
                        self[row_name, col_name] = f(self[row_name, col_name])

    def make_programatic_column_with(self, f, column):
        # TODO could add colname and add values directly to final report **mind not handle issues well**
        new_rows = pe.Sheet()
        new_rows.row += [column]
        # self.colnames += column
        for row in self.rows():
            row_w_headers = dict(zip(self.colnames, row))
            new_rows.row += f(row_w_headers)
        self.column += new_rows

    def __setitem__(self, key, value):
        try:
            super().__setitem__((self.rownames.index(key[0]), self.colnames.index(key[1])), value)
        except AttributeError:
            print('attriberror setkey')
