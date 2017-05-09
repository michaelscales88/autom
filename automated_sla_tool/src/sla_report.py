import operator
from datetime import time, timedelta, date
from dateutil.parser import parse
from collections import defaultdict, OrderedDict


# TODO all instances that are being used should come from factory
from automated_sla_tool.src.bucket_dict import BucketDict
from automated_sla_tool.src.a_report import AReport
from automated_sla_tool.src.utilities import valid_dt
from automated_sla_tool.src.factory import get_vm

from json import dumps


class SlaReport(AReport):
    def __init__(self, report_date=None, test_mode=False):
        super().__init__(rpt_inr=report_date, test_mode=test_mode)
        if not self.test_mode and self.check_finished(sub_dir=self.settings['sub_dir_fmt'],
                                                      report_string=self.settings['file_fmt']):
            print('Report Complete for {date}'.format(date=self.interval))
        else:
            print('Building a report for {date}'.format(date=self.interval))
            self.load_and_prepare()
            self.sla_report = {}
            # self.run()

    '''
    UI Section
    '''

    def __doc__(self):
        # Allows use of inspect.isclass
        pass

    def run(self):
        if self.output.finished:
            return
        else:
            self.extract_report_information()
            self.process_report()
            self.validate_final_report()
            self.save()

    def run_test(self):
        self.process_report2()

    def manual_input(self):
        input_opt = OrderedDict(
            [
                ('-4 Days', -4),
                ('-3 Days', -3),
                ('-2 Days', -2),
                ('Yesterday', -1)
            ]
        )
        return date.today() + timedelta(days=self.util.return_selection(input_opt))

    def load_and_prepare(self):
        # TODO https://github.com/pyexcel/pyexcel-xlsx: add io stream for opening xlsx instead of saving a copy
        super().load()
        call_details_filters = [
            self.util.inbound_call_filter,
            self.util.zero_duration_filter,
            self.util.remove_internal_inbound_filter
        ]
        self.src_files[r'Call Details'] = self.util.collate_wb_to_sheet(wb=self.src_files[r'Call Details'])
        self.util.apply_format_to_sheet(sheet=self.src_files[r'Call Details'],
                                        filters=call_details_filters)
        self.compile_call_details()
        self.src_files[r'Call Details'].name = 'call_details'   # this is a hack for the Client Accum
        self.src_files[r'Group Abandoned Calls'] = self.util.collate_wb_to_sheet(
            wb=self.src_files[r'Group Abandoned Calls']
        )
        self.util.apply_format_to_sheet(sheet=(self.src_files[r'Group Abandoned Calls']),
                                        one_filter=self.util.answered_filter)
        self.scrutinize_abandon_group()
        if not self.test_mode:
            self.src_files[r'Voice Mail'] = self.modify_vm(get_vm(self))
        # else:
        #     self.src_files[r'Voice Mail'] = get_vm(self)

    def new_run(self):
        ans_cid_by_client = self.group_cid_by_client(self.src_files[r'Call Details'])
        lost_cid_by_client = self.group_cid_by_client(self.src_files[r'Group Abandoned Calls'])
        print(ans_cid_by_client)
        print(lost_cid_by_client)
        print(self.src_files[r'Voice Mail'])
        # TODO: this should be generator that handles full_service or normal day of the week
        # TODO 2: AppSettings needs to autodetect int, bool, ts, text etc
        for client_name, client_details in self._settings['Clients'].items():
            print(client_details['client_num'])
            vm = self.src_files[r'Voice Mail'].get(client_name, [])
            calls_ans = ans_cid_by_client.get(int(client_details['client_num']), [])
            calls_lost = lost_cid_by_client.get(int(client_details['client_num']), [])
            print(client_name)
            print(vm)
            print(calls_ans)
            print(calls_lost)

    # TODO refactor this: combine process and extract and remove client -> call it run
    def extract_report_information(self):
        if self.output.finished or self.test_mode:
            return
        else:
            ans_cid_by_client = self.group_cid_by_client(self.src_files[r'Call Details'])
            lost_cid_by_client = self.group_cid_by_client(self.src_files[r'Group Abandoned Calls'])
            for client, client_num, full_service in self.process_gen('Clients'):
                self.sla_report[client_num] = Client(
                    name=client_num,
                    answered_calls=ans_cid_by_client.get(client_num, []),
                    lost_calls=lost_cid_by_client.get(client_num, []),
                    voicemail=self.src_files[r'Voice Mail'].get(client, []),
                    full_service=full_service
                )
                if not self.sla_report[client_num].is_empty():
                    # TODO this could perhaps be a try: ... KeyError...
                    if self.sla_report[client_num].no_answered() is False:
                        self.sla_report[client_num].extract_call_details(self.src_files[r'Call Details'])
                    if self.sla_report[client_num].no_lost() is False:
                        self.sla_report[client_num].extract_abandon_group_details(
                            self.src_files[r'Group Abandoned Calls'])

    def process_report(self):
        if self.output.finished or self.test_mode:
            return
        else:
            is_weekday = self.util.is_weekday(self.interval)
            headers = [self.interval.strftime('%A %m/%d/%Y'), 'I/C Presented', 'I/C Answered', 'I/C Lost',
                       'Voice Mails',
                       'Incoming Answered (%)', 'Incoming Lost (%)', 'Average Incoming Duration',
                       'Average Wait Answered',
                       'Average Wait Lost', 'Calls Ans Within 15', 'Calls Ans Within 30', 'Calls Ans Within 45',
                       'Calls Ans Within 60', 'Calls Ans Within 999', 'Call Ans + 999', 'Longest Waiting Answered',
                       'PCA']
            self.output.row += headers
            self.output.name_columns_by_row(0)
            total_row = dict((value, 0) for value in headers[1:])
            total_row['Label'] = 'Summary'
            for client, client_num, full_service in self.process_gen('Clients'):
                if is_weekday or full_service:
                    num_calls = self.sla_report[client_num].get_number_of_calls()
                    this_row = dict((value, 0) for value in headers[1:])
                    this_row['I/C Presented'] = sum(num_calls.values())
                    this_row['Label'] = '{num} {name}'.format(num=client_num, name=client)
                    if this_row['I/C Presented'] > 0:
                        ticker_stats = self.sla_report[client_num].get_call_ticker()
                        this_row['I/C Answered'] = num_calls['answered']
                        this_row['I/C Lost'] = num_calls['lost']
                        this_row['Voice Mails'] = num_calls['voicemails']
                        this_row['Incoming Answered (%)'] = (num_calls['answered'] / this_row['I/C Presented'])
                        this_row['Incoming Lost (%)'] = (
                            (num_calls['lost'] + num_calls['voicemails']) / this_row['I/C Presented'])
                        this_row['Average Incoming Duration'] = self.sla_report[client_num].get_avg_call_duration()
                        this_row['Average Wait Answered'] = self.sla_report[client_num].get_avg_wait_answered()
                        this_row['Average Wait Lost'] = self.sla_report[client_num].get_avg_lost_duration()
                        this_row['Calls Ans Within 15'] = ticker_stats[15]
                        this_row['Calls Ans Within 30'] = ticker_stats[30]
                        this_row['Calls Ans Within 45'] = ticker_stats[45]
                        this_row['Calls Ans Within 60'] = ticker_stats[60]
                        this_row['Calls Ans Within 999'] = ticker_stats[999]
                        this_row['Call Ans + 999'] = ticker_stats[999999]
                        this_row['Longest Waiting Answered'] = self.sla_report[client_num].get_longest_answered()
                        try:
                            this_row['PCA'] = ((ticker_stats[15] + ticker_stats[30]) / num_calls['answered'])
                        except ZeroDivisionError:
                            this_row['PCA'] = 0

                        self.accumulate_total_row(this_row, total_row)
                        self.add_row(this_row)
                    else:
                        self.add_row(this_row)
            self.finalize_total_row(total_row)
            self.add_row(total_row)
            self.output.name_rows_by_column(0)
            self.output.finished = True

    def extract_report_information2(self):
        if self.output.finished or self.test_mode:
            return
        else:
            ans_cid_by_client = self.group_cid_by_client(self.src_files[r'Call Details'])
            lost_cid_by_client = self.group_cid_by_client(self.src_files[r'Group Abandoned Calls'])

            for client, client_num, full_service in self.process_gen('Clients'):
                self.sla_report[client_num] = Client(
                    name=client_num,
                    answered_calls=ans_cid_by_client.get(client_num, []),
                    lost_calls=lost_cid_by_client.get(client_num, []),
                    voicemail=self.src_files[r'Voice Mail'].get(client, []),
                    full_service=full_service
                )
                if not self.sla_report[client_num].is_empty():
                    # TODO this could perhaps be a try: ... KeyError...
                    if self.sla_report[client_num].no_answered() is False:
                        self.sla_report[client_num].extract_call_details(self.src_files[r'Call Details'])
                    if self.sla_report[client_num].no_lost() is False:
                        self.sla_report[client_num].extract_abandon_group_details(
                            self.src_files[r'Group Abandoned Calls'])

    # def mask(self):
    #     # TODO to abstract the report excel/sql headers need to link to a program header
    #     # Ex .Ini
    #     # SLA event_duration = Total Duration
    #     # pivots the values to the keywords provided
    #     # for each row in the src data add row/keyword "pivot value"
    #     # this creates a report of target headers for each row
    #     # row names can be specified in user documentation
    #     pass

    # TODO pyexcel auto dt, int, and strings for summing timestamps
    # TODO 2: this will require adding Schema Event Type conversion data to work for dB and src doc
    def process_report2(self):
        translator = {
            value['client_num']: key for key, value in self.settings['Clients'].items()
        }
        print('applying format')
        for sheet in self.src_files['Cradle to Grave']:
            try:
                sheet.column.format('Event Duration', self.util.to_td)
                sheet.column.format('Start Time', self.util.to_dt)
                sheet.column.format('End Time', self.util.to_dt)
            except Exception as e:
                print(e, 'Error Motherfreaker')
        print('testing format')
        self.data_center.job = self
        print('about to iterate data center')
        print('**Call Details**')
        for sheet_name, data_dict in self.data_center:
            if data_dict['Answered']:
                print(sheet_name)
                self.data_center.print_record(data_dict)

        print('**Group Abandoned**')
        for sheet_name, data_dict in self.data_center:
            if not data_dict['Answered']:
                print(sheet_name)
                self.data_center.print_record(data_dict)

        # print('**VERIFY VM**')
        # self.data_center.print_record(self.src_files[r'Voice Mail']['Danaher'])
        #
        # print('**Unverified Voicemail**')
        # for sheet_name, data_dict in self.data_center:
        #     if data_dict['Voicemail']:
        #         # print(sheet_name)
        #         # self.data_center.print_record(data_dict)
        #         client_num = data_dict['Receiving Party']
        #         # print('Trying to get client_name for', client_num)
        #         client_name = translator.get(client_num, None)
        #         # print('getting data for', client_name)
        #         voicemail_data = self.src_files[r'Voice Mail'].get(client_name, None)
        #         # print('Got data for', voicemail_data)
        #         if voicemail_data:
        #             # print('checking whether', data_dict['Calling Party'], 'is in vm_data')
        #             call_instance = [d for d in voicemail_data if d['phone_number'] == data_dict['Calling Party']]
        #             # call_instance = voicemail_data.get(data_dict['Calling Party'], None)
        #             # print('This is my call instance', call_instance)
        #             if call_instance and abs(call_instance[0]['time'] - data_dict['End Time']) < timedelta(seconds=30):
        #                 # print(call_instance)
        #                 self.data_center.verified(sheet_name, 'Voicemail')
        #                 # print('Claiming I set vm to verified for', sheet_name)
        #
        # i_count = {}
        # print('**Verified Voicemail**')
        # for sheet_name, data_dict in self.data_center:
        #     if data_dict['Voicemail'] == 'Verified':
        #         if data_dict['Receiving Party'] == 7545:
        #             print(sheet_name)
        #
        #         # print(sheet_name)
        #         # self.data_center.print_record(data_dict)
        #         dup_info = i_count.get(
        #             data_dict['Receiving Party'], {
        #                 'count': 0
        #             }
        #         )
        #         dup_info['count'] += 1
        #         i_count[data_dict['Receiving Party']] = dup_info
        #
        # self.data_center.print_record(i_count)
        # for sheet_name, data_dict in {sheet_name: data_dict for sheet_name, data_dict in self.data_center
        #                               if data_dict['Receiving Party'] == 7545 and data_dict['Voicemail'] == 'Verified'
        #                               }.items():
        #     print(sheet_name)
        #     self.data_center.print_record(data_dict)
        # print('completed iterating data center')

    def __getitem__(self, item):
        pass

    def __repr__(self):
        return '{module} {unique}'.format(module=self.__module__, unique=self.interval)

    '''
    SlaReport Functions
    '''

    def process_gen(self, lvl):
        for key, items in self.settings[lvl].items():
            yield (key,) + tuple(items[item] for item in items.keys())

    def compile_call_details(self):
        if self.output.finished:
            return
        else:
            hold_events = ('Hold', 'Transfer Hold', 'Park')
            additional_columns = OrderedDict(
                [
                    ('Wait Time', []),
                    ('Hold Time', [])
                ]
            )
            for row_name in self.src_files[r'Call Details'].rownames:
                unhandled_call_data = {
                    k: 0 for k in hold_events
                    }
                tot_call_duration = self.util.get_sec(self.src_files[r'Call Details'][row_name, 'Call Duration'])
                talk_duration = self.util.get_sec(self.src_files[r'Call Details'][row_name, 'Talking Duration'])
                call_id = row_name.replace(':', ' ')
                cradle_sheet = self.src_files[r'Cradle to Grave'][call_id]
                for event_row in cradle_sheet.rownames:
                    event_type = cradle_sheet[event_row, 'Event Type']
                    if event_type in hold_events:
                        unhandled_call_data[event_type] += self.util.get_sec(cradle_sheet[event_row, 'Event Duration'])
                raw_hold_time = sum(val for val in unhandled_call_data.values())
                raw_time_waited = tot_call_duration - talk_duration - raw_hold_time
                additional_columns['Hold Time'].append(self.util.convert_time_stamp(raw_hold_time))
                additional_columns['Wait Time'].append(self.util.convert_time_stamp(raw_time_waited))
            self.src_files[r'Call Details'].extend_columns(additional_columns)

    def scrutinize_abandon_group(self):
        if self.output.finished:
            return
        else:
            self.remove_calls_less_than_twenty_seconds()
            self.remove_non_distinct_callers()

    # TODO combine remove non-distinct and calls <20 into general filter function to remove multiple for loops
    def remove_non_distinct_callers(self):
        i_count = self.util.find_non_distinct(sheet=self.src_files[r'Group Abandoned Calls'],
                                              event_col='External Party')
        for dup_val, dup_call_ids in {k: reversed(sorted(v['rows']))
                                      for k, v in i_count.items() if v['count'] > 1}.items():
            for call_id in dup_call_ids:
                try:
                    prev_call = self.parse_to_sec(
                        self.src_files[r'Group Abandoned Calls'][next(dup_call_ids), 'End Time']
                    )
                except StopIteration:
                    pass  # end
                else:
                    last_call = self.parse_to_sec(self.src_files[r'Group Abandoned Calls'][call_id, 'Start Time'])
                    if abs(last_call - prev_call) <= 60:
                        self.src_files[r'Group Abandoned Calls'].delete_named_row_at(call_id)

    def remove_calls_less_than_twenty_seconds(self):
        for row_name in reversed(self.src_files[r'Group Abandoned Calls'].rownames):
            call_duration = self.util.get_sec(self.src_files[r'Group Abandoned Calls'][row_name, 'Call Duration'])
            if call_duration < 20:
                self.src_files[r'Group Abandoned Calls'].delete_named_row_at(row_name)

    def validate_final_report(self):
        for row in self.output.rownames:
            ticker_total = 0
            answered = self.output[row, 'I/C Answered']
            ticker_total += self.output[row, 'Calls Ans Within 15']
            ticker_total += self.output[row, 'Calls Ans Within 30']
            ticker_total += self.output[row, 'Calls Ans Within 45']
            ticker_total += self.output[row, 'Calls Ans Within 60']
            ticker_total += self.output[row, 'Calls Ans Within 999']
            ticker_total += self.output[row, 'Call Ans + 999']
            if answered != ticker_total:
                raise ValueError('Validation error ->'
                                 'ticker total != answered for: '
                                 '{0}'.format(row[0]))

    # TODO generalize this to group reports by col/type
    # TODO 2: push into ReportUtilities
    def group_cid_by_client(self, report):
        report_details = defaultdict(list)
        for row_name in report.rownames:
            try:
                client = int(report[row_name, 'Internal Party'])
            except ValueError:
                client = self.handle_read_value_error(row_name)
            finally:
                report_details[client].append(row_name)
        return report_details

    # TODO modify naming for this and new_type_cradle...
    def modify_vm(self, inc_data):
        rtn_dict = {}
        if isinstance(inc_data, dict):
            c_vm = self.new_type_cradle_vm()
            for client_name, inc_data, c_vm in sorted(self.util.common_keys(inc_data, c_vm)):
                if client_name == 'Danaher':
                    self.data_center.print_record(inc_data)
                    self.data_center.print_record(c_vm)
                for match1, match2 in self.util.return_matches(inc_data, c_vm, match_val='phone_number'):
                    if abs(match1['time'] - match2['time']) < timedelta(seconds=30):
                        call_id = match1['call_id'] if match1.get('call_id', None) else match2['call_id']
                        client_info = rtn_dict.get(client_name, [])
                        client_info.append(call_id)
                        rtn_dict[client_name] = client_info
                        if client_name == 'Danaher':
                            print('matched danaher call_id', call_id)
        return rtn_dict

    def new_type_cradle_vm(self):
        voice_mail_dict = defaultdict(list)
        for call_id_page in self.src_files[r'Cradle to Grave']:
            for row_name in call_id_page.rownames:
                row_event = call_id_page[row_name, 'Event Type']
                if 'Voicemail' in row_event:
                    receiving_party = call_id_page[row_name, 'Receiving Party']
                    if receiving_party.isalpha():
                        # print('alpha {rp}'.format(rp=receiving_party))
                        # check if this is a valid client
                        pass  # should pass if client name is here
                    else:
                        # print('non-alpha {rp}'.format(rp=receiving_party))
                        # should catch blanks and clients in ext fmt
                        # print('need a way to fix blanks and numbers')
                        pass
                    client_info = voice_mail_dict.get(receiving_party, [])
                    try:
                        # TODO: phone_number might be faster lookup as an integer
                        a_vm = {
                            'phone_number': self.util.phone_number(call_id_page[row_name, 'Calling Party']),
                            'call_id': call_id_page.name,
                            'time': valid_dt(call_id_page[row_name, 'End Time'])
                        }
                        client_info.append(a_vm)
                        voice_mail_dict[receiving_party] = client_info
                    except TypeError:
                        print(call_id_page[row_name, 'Calling Party'])
                        raise
        return voice_mail_dict

    '''
    Utilities Section
    '''

    def add_row(self, a_row):
        self.format_row(a_row)
        self.output.row += self.return_row_as_list(a_row)

    def format_row(self, row):
        row['Average Incoming Duration'] = self.util.convert_time_stamp(row['Average Incoming Duration'])
        row['Average Wait Answered'] = self.util.convert_time_stamp(row['Average Wait Answered'])
        row['Average Wait Lost'] = self.util.convert_time_stamp(row['Average Wait Lost'])
        row['Longest Waiting Answered'] = self.util.convert_time_stamp(row['Longest Waiting Answered'])
        row['Incoming Answered (%)'] = '{0:.1%}'.format(row['Incoming Answered (%)'])
        row['Incoming Lost (%)'] = '{0:.1%}'.format(row['Incoming Lost (%)'])
        row['PCA'] = '{0:.1%}'.format(row['PCA'])

    @staticmethod
    def return_row_as_list(row):
        return [row['Label'],
                row['I/C Presented'],
                row['I/C Answered'],
                row['I/C Lost'],
                row['Voice Mails'],
                row['Incoming Answered (%)'],
                row['Incoming Lost (%)'],
                row['Average Incoming Duration'],
                row['Average Wait Answered'],
                row['Average Wait Lost'],
                row['Calls Ans Within 15'],
                row['Calls Ans Within 30'],
                row['Calls Ans Within 45'],
                row['Calls Ans Within 60'],
                row['Calls Ans Within 999'],
                row['Call Ans + 999'],
                row['Longest Waiting Answered'],
                row['PCA']]

    @staticmethod
    def accumulate_total_row(row, tr):
        tr['I/C Presented'] += row['I/C Presented']
        tr['I/C Answered'] += row['I/C Answered']
        tr['I/C Lost'] += row['I/C Lost']
        tr['Voice Mails'] += row['Voice Mails']
        tr['Average Incoming Duration'] += row['Average Incoming Duration'] * row['I/C Answered']
        tr['Average Wait Answered'] += row['Average Wait Answered'] * row['I/C Answered']
        tr['Average Wait Lost'] += row['Average Wait Lost'] * row['I/C Lost']
        tr['Calls Ans Within 15'] += row['Calls Ans Within 15']
        tr['Calls Ans Within 30'] += row['Calls Ans Within 30']
        tr['Calls Ans Within 45'] += row['Calls Ans Within 45']
        tr['Calls Ans Within 60'] += row['Calls Ans Within 60']
        tr['Calls Ans Within 999'] += row['Calls Ans Within 999']
        tr['Call Ans + 999'] += row['Call Ans + 999']
        if tr['Longest Waiting Answered'] < row['Longest Waiting Answered']:
            tr['Longest Waiting Answered'] = row['Longest Waiting Answered']

    @staticmethod
    def finalize_total_row(tr):
        if tr['I/C Presented'] > 0:
            tr['Incoming Answered (%)'] = operator.truediv(tr['I/C Answered'],
                                                           tr['I/C Presented'])
            tr['Incoming Lost (%)'] = operator.truediv(tr['I/C Lost'] + tr['Voice Mails'],
                                                       tr['I/C Presented'])
            tr['PCA'] = operator.truediv(tr['Calls Ans Within 15'] + tr['Calls Ans Within 30'],
                                         tr['I/C Presented'])
            if tr['I/C Answered'] > 0:
                tr['Average Incoming Duration'] = operator.floordiv(tr['Average Incoming Duration'],
                                                                    tr['I/C Answered'])
                tr['Average Wait Answered'] = operator.floordiv(tr['Average Wait Answered'],
                                                                tr['I/C Answered'])
            if tr['I/C Lost'] > 0:
                tr['Average Wait Lost'] = operator.floordiv(tr['Average Wait Lost'],
                                                            tr['I/C Lost'])

    def handle_read_value_error(self, call_id):
        sheet = self.src_files[r'Cradle to Grave'][call_id.replace(':', ' ')]
        hunt_index = sheet.column['Event Type'].index('Ringing')
        return sheet.column['Receiving Party'][hunt_index]


class Client:
    earliest_call = time(hour=7)
    latest_call = time(hour=20)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.full_service = kwargs.get('full_service', False)
        self.answered_calls = kwargs.get('answered_calls', [])
        self.lost_calls = kwargs.get('lost_calls', [])
        self.voicemails = kwargs.get('voicemail', [])
        self.remove_voicemails()
        self.longest_answered = 0
        self.call_details_duration = timedelta(seconds=0)
        self.abandon_group_duration = timedelta(seconds=0)
        self.wait_answered = []
        self.call_details_ticker = BucketDict(
            {(-1, 15): 0, (15, 30): 0, (30, 45): 0, (45, 60): 0, (60, 999): 0, (999, 999999): 0}
        )

    def __str__(self):
        print('name: {}'.format(self.name))
        print('ans: {}'.format(self.answered_calls))
        print('lost: {}'.format(self.lost_calls))
        print('vm: {}'.format(self.voicemails))

    def remove_voicemails(self):
        '''
        Should never find a voicemail call since they're excluded when Call Details loads
        :return:
        '''
        for voicemail in self.voicemails:
            if voicemail in self.lost_calls:
                self.lost_calls.remove(voicemail)
            if voicemail in self.answered_calls:
                self.answered_calls.remove(voicemail)

    def is_empty(self):
        return len(self.answered_calls) == 0 and len(self.lost_calls) == 0 and len(self.voicemails) == 0

    def no_answered(self):
        return len(self.answered_calls) == 0

    def no_lost(self):
        return len(self.lost_calls) == 0

    @staticmethod
    def convert_datetime_seconds(datetime_obj):
        return 60 * (datetime_obj.hour * 60) + datetime_obj.minute * 60 + datetime_obj.second

    def extract_call_details(self, call_details):
        self.call_details_duration = self.read_report(report=call_details,
                                                      call_group=self.answered_calls,
                                                      call_ticker=self.call_details_ticker,
                                                      wait_answered=self.wait_answered)

    def extract_abandon_group_details(self, abandon_group):
        self.abandon_group_duration = self.read_report(report=abandon_group,
                                                       call_group=self.lost_calls)

    def read_report(self, report=None, call_group=None, call_ticker=None, wait_answered=None):
        duration_counter = timedelta(seconds=0)
        for call_id in reversed(call_group):
            start_time = report[call_id, 'Start Time']
            if self.valid_time(parse(start_time)) or self.full_service:
                duration_datetime = parse(report[call_id, 'Call Duration'])
                converted_seconds = self.convert_datetime_seconds(duration_datetime)
                if report.name == 'call_details' or converted_seconds >= 20:
                    duration_counter += timedelta(seconds=converted_seconds)
                    if call_ticker is not None:
                        hold_duration = parse(report[call_id, 'Wait Time'])
                        hold_duration_seconds = self.convert_datetime_seconds(hold_duration)
                        wait_answered.append(hold_duration_seconds)
                        call_ticker.add_range_item(hold_duration_seconds)
                        if hold_duration_seconds > self.longest_answered:
                            self.longest_answered = hold_duration_seconds
                else:
                    call_group.remove(call_id)
            else:
                call_group.remove(call_id)
        return duration_counter

    def valid_time(self, call_datetime):
        # TODO: call ID are ordered -> check first and last instead of whole call_ID list
        call_time = call_datetime.time()
        return self.earliest_call <= call_time <= self.latest_call

    def get_longest_answered(self):
        return self.longest_answered

    def get_avg_call_duration(self):
        return self.get_avg_duration(current_duration=self.call_details_duration.total_seconds(),
                                     call_group=self.answered_calls)

    def get_avg_lost_duration(self):
        return self.get_avg_duration(current_duration=self.abandon_group_duration.total_seconds(),
                                     call_group=self.lost_calls)

    def get_avg_wait_answered(self):
        return self.get_avg_duration(current_duration=sum(self.wait_answered),
                                     call_group=self.wait_answered)

    @staticmethod
    def get_avg_duration(current_duration=None, call_group=None):
        return_value = current_duration
        try:
            return_value //= len(call_group)
        except ZeroDivisionError:
            pass
        return int(return_value)

    def get_number_of_calls(self):
        return {
            'answered': len(self.answered_calls),
            'lost': len(self.lost_calls),
            'voicemails': len(self.voicemails)
        }

    def get_call_ticker(self):
        return self.call_details_ticker

    def is_full_service(self):
        return self.full_service
