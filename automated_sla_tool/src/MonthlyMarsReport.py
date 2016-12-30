import traceback
import time
import pyexcel as pe
import multiprocessing as mp
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from automated_sla_tool.src.DailyMarsReport import DailyMarsReport
from automated_sla_tool.src.AReport import AReport
from automated_sla_tool.src.TupleKeyDict import TupleKeyDict
from automated_sla_tool.src.ReportModel import ReportModel
from automated_sla_tool.src.ReportDispatcher import ReportDispatcher as Dispatch


class MonthlyMarsReport(AReport):
    def __init__(self, month):
        # TODO improve report_dates to be a month and run for the month until not the month
        super().__init__(report_dates=month,
                         report_type='monthly_mars_report')
        self.report_model = pe.Book()
        self.final_report_fields = ['Absent', 'Late', 'DND Duration', 'Duration', 'numDND', 'Inbound Ans',
                                    'Inbound Lost', 'Outbound', 'Inbound Duration', 'Outbound Duration']

    '''
    UI Section
    '''

    def run(self):
        # TODO Make this a dispatcher -> threading
        run_date = datetime.strptime(self.dates, '%B').date().replace(year=2016)
        end_date = run_date + relativedelta(months=1)
        while run_date < end_date:
            try:
                try:
                    file = DailyMarsReport(day=run_date)
                    file.save()
                except (OSError, FileNotFoundError) as e:
                    print('Could not open report for date {}'.format(run_date))
                    print(e)
                except SystemExit:
                    raise SystemExit('SysExiting MARsReport...')
                except Exception:
                    print('Unexpected Exception encounter: {}'.format(run_date.strftime("%m%d%Y")))
                    import sys
                    error = traceback.format_exc()
                    traceback.print_exc(file=sys.stderr)
                    print(error)
                else:
                    print("Program ran successfully for date: {}".format(run_date.strftime("%m%d%Y")))
                    self.report_model += file.transmit_report()
            except SystemExit:
                pass
            finally:
                run_date += timedelta(days=1)
        try:
            self.prep_sheets()
        except IndexError:
            pass
        else:
            self.summarize_queue()

    def print_queue(self):
        print(self.report_model)

    def summarize_queue(self):
        if self.is_empty_wb(self.report_model):
            return
        agent_summary = AgentSummary(fields=self.final_report_fields)
        for report in self.report_model:
            for agent in report.rownames:
                if agent == 'Notes':
                    break
                agent_summary.collect_data(agent, report)
        self.set_final_report(agent_summary)

    '''
    Utilities Section
    '''

    def prep_sheets(self):
        for sheet in self.report_model:
            sheet.name_rows_by_column(0)
            sheet.name_columns_by_row(0)

    def set_final_report(self, report_summary):
        self.fr.set_header(report_summary.get_header())
        for (agent, data) in report_summary.items():
            row = [agent] + [data[k] for k in sorted(data.keys())]
            self.fr.row += row
        self.fr.make_programatic_column_with(self.calculate_avail, "Avail")
        self.fr.format_columns_with(self.convert_time_stamp, "Duration")
        print(self.fr)

    def create_sheet(self, headers):
        sheet = pe.Sheet()
        sheet.row += headers
        sheet.name_columns_by_row(0)
        return sheet

    def save_report(self):
        self.set_save_path('monthly_mars_report')
        the_file = r'{0}_mars_report'.format(self.dates.strftime('%B'))
        self.fr.day = self.dates.strftime('%B %Y')
        file_string = r'.\{0}.xlsx'.format(the_file)
        self.fr.save_as(filename=file_string)

    def calculate_avail(self, row):
        rtn_val = [r'{0:.1%}'.format(0)]
        try:
            p_avail = ((row["Duration"] - row["DND Duration"]) /
                       row["Duration"])
            rtn_val = [r'{0:.1%}'.format(p_avail)]
        except (ZeroDivisionError, KeyError) as e:
            print('passing calculate avail bc of {}'.format(e))
        return rtn_val


class AgentSummary(TupleKeyDict):
    def __init__(self, fields=None):
        super().__init__()
        self._fields = fields

    @property
    def fields(self):
        return self._fields

    def get_header(self):
        return ['Employee'] + sorted(self.fields)

    def collect_data(self, agent, report):
        for column in self.fields:
            try:
                key = (agent, column)
                add_val = report[agent, column]
                try:
                    add_val = int(
                        timedelta(hours=add_val.hour, minutes=add_val.minute, seconds=add_val.second).total_seconds())
                except AttributeError:
                    pass

                try:
                    self[key] += add_val
                except KeyError:
                    super().__setitem__(key, add_val)
            except ValueError:
                print('Could not retrieve field: <{0}> '
                      'from file: {1}'.format(column, report.day))
            #
            #
            #
            #
            #
            # try:
            #     self.__setitem__((agent, column), report[agent, column])
            # except ValueError:
            #     print('Could not retrieve field: <{0}> '
            #           'from file: {1}'.format(column, report.name))
