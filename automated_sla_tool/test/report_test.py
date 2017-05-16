from datetime import datetime, timedelta
import datetime as dt
from pyexcel import Sheet
from collections import OrderedDict
from json import dumps
from itertools import groupby, chain

from automated_sla_tool.test.PG_json_test import session_data
from automated_sla_tool.test.flexible_storage import MyEncoder
from automated_sla_tool.src.app_settings import AppSettings
from automated_sla_tool.src.report_utilities import ReportUtilities

_settings = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\automated_sla_tool\settings\db_report_test'


def main():
    output_headers = [
        'I/C Presented',
        'I/C Answered',
        'I/C Lost',
        'Voice Mails',
        'Incoming Answered (%)',
        'Incoming Lost (%)',
        'Average Incoming Duration',
        'Average Wait Answered',
        'Average Wait Lost',
        'Calls Ans Within 15',
        'Calls Ans Within 30',
        'Calls Ans Within 45',
        'Calls Ans Within 60',
        'Calls Ans Within 999',
        'Call Ans + 999',
        'Longest Waiting Answered',
        'PCA'
    ]

    settings = AppSettings(file_name=_settings)
    test_output = Sheet(
        colnames=output_headers
    )

    for client_num in settings['Clients']:
        additional_row = OrderedDict(
            [
                (client_num,
                 [0, 0, 0, 0, 0, 0, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0, 0, 0, timedelta(0), 0]
                 )
            ]
        )
        test_output.extend_rows(additional_row)

    records = session_data(datetime.today().date().replace(year=2017, month=5, day=1))

    # Filter Step
    # for key, group in groupby(records, lambda item: item.unique_id):
    #     print(key)
    #     print([item.id for item in group])

    i_count = {}
    for record in records:
        # print(record.id, record.unique_id2, record.unique_id1)
        dup_event = i_count.get(
            record.unique_id2, {
                'count': 0,
                'call_id': []
            }
        )
        dup_event['count'] += 1
        dup_event['call_id'].append(record.id)

        i_count[record.unique_id2] = dup_event

    # print(dumps(i_count, indent=4))
    print(len(records))
    potential_duplicates = []
    for k, v in i_count.items():
        if v['count'] > 1:
            potential_duplicates.append(v['call_id'])
    print(len(potential_duplicates), potential_duplicates)
    print(records)
    for call_ids in potential_duplicates:
        print('searching', [call_id for call_id in reversed(call_ids)])
        for call_id in reversed(call_ids):
            for x in records:
                if x.id == call_id:
                    print("i found it!")
                    print(x.id)
                    break
        # try:
        #     prev_call = records[next(potential_duplicates)]
        # except (StopIteration, IndexError) as e:
        #     print(e, call_ids)  # end
        # else:
        #     try:
        #         last_call = records[call_ids]
        #         print("**NOTE IM COMPARING**")
        #         # print(prev_call)
        #         # print(last_call)
        #         if abs(last_call.start - prev_call.end) <= timedelta(seconds=60):
        #             print('i deleted some duplicates')
        #             del records[call_ids]
        #     except IndexError as e:
        #         print('Index Error', call_ids)

    # Process Step
    for record in records:
        row_name = str(record.unique_id1)    # This is how we bind our client settings
        if row_name in test_output.rownames:
            call_summary = {}
            for event_id, event in sorted(record.data['Events'].items()):
                event_accum = call_summary.get(
                    event['event_type'],
                    timedelta(0)
                )
                event_accum += event['end_time'] - event['start_time']
                call_summary[event['event_type']] = event_accum

            # summary_of_calls[record.id] = call_summary
            call_duration = record.end - record.start
            talking_time = call_summary.get(4, timedelta(0))
            voicemail_time = call_summary.get(10, timedelta(0))
            hold_time = sum(
                [call_summary.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time
            # DO the rest of the output work
            if talking_time > timedelta(0):
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Answered'] += 1
                test_output[row_name, 'Average Incoming Duration'] += talking_time
                test_output[row_name, 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    test_output[row_name, 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    test_output[row_name, 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    test_output[row_name, 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    test_output[row_name, 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    test_output[row_name, 'Calls Ans Within 999'] += 1

                else:
                    test_output[row_name, 'Call Ans + 999'] += 1

                if wait_duration > test_output[row_name, 'Longest Waiting Answered']:
                    test_output[row_name, 'Longest Waiting Answered'] = wait_duration

            elif voicemail_time > timedelta(seconds=20):
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'Voice Mails'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

            elif call_duration > timedelta(seconds=20):
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Lost'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

            else:
                pass


    # Update output from data source
    # for record in records:
    #     call_group = str(record.data['Call Group'])
    #     client_data = settings['Clients'].get(call_group, None)  # Determine if this is a valid client/track 24 hr cli
    #     call_duration = record.data['End Time'] - record.data['Start Time']
    #     wait_duration = call_duration - record.data['Talking Duration']
    #     print(call_group, wait_duration)
    #     if client_data and (record.start.time() > dt.time()):
    #         print(dumps(record.data, cls=MyEncoder))
    #         if record.data['Answered']:
    #             # Do answered work
    #             test_output[call_group, 'I/C Answered'] += 1
    #             test_output[call_group, 'I/C Presented'] += 1
    #             test_output[call_group, 'Average Incoming Duration'] += record.data['Talking Duration']
    #             test_output[call_group, 'Average Wait Answered'] += wait_duration
    #             if call_group == '7521':
    #                 print('SWS duration', record.id, wait_duration)
    #
    #             # Qualify calls by duration
    #             if wait_duration <= timedelta(seconds=15):
    #                 test_output[call_group, 'Calls Ans Within 15'] += 1
    #
    #             elif wait_duration <= timedelta(seconds=30):
    #                 test_output[call_group, 'Calls Ans Within 30'] += 1
    #
    #             elif wait_duration <= timedelta(seconds=45):
    #                 test_output[call_group, 'Calls Ans Within 45'] += 1
    #
    #             elif wait_duration <= timedelta(seconds=60):
    #                 test_output[call_group, 'Calls Ans Within 60'] += 1
    #
    #             elif wait_duration <= timedelta(seconds=999):
    #                 test_output[call_group, 'Calls Ans Within 999'] += 1
    #
    #             else:
    #                 test_output[call_group, 'Call Ans + 999'] += 1
    #
    #             if not test_output[call_group, 'Longest Waiting Answered']:
    #                 test_output[call_group, 'Longest Waiting Answered'] = wait_duration
    #             elif wait_duration > test_output[call_group, 'Longest Waiting Answered']:
    #                 test_output[call_group, 'Longest Waiting Answered'] = wait_duration
    #
    #         else:
    #             # Do lost work
    #             if record.data['Voicemail'] and record.data['Voicemail'] > timedelta(seconds=20):
    #                 test_output[call_group, 'Voice Mails'] += 1
    #                 test_output[call_group, 'I/C Presented'] += 1
    #
    #             elif (record.data['End Time'] - record.data['Start Time']) > timedelta(seconds=20):
    #                 test_output[call_group, 'I/C Lost'] += 1
    #                 test_output[call_group, 'I/C Presented'] += 1
    #                 test_output[call_group, 'Average Wait Lost'] += call_duration
    #
    #             else:
    #                 print('didnt count')

    # Update programmatic columns
    # Finalize Step
    for row in test_output.rownames:
        try:
            test_output[row, 'Incoming Answered (%)'] = test_output[row, 'I/C Answered'] / test_output[
                row, 'I/C Presented']
        except ZeroDivisionError:
            test_output[row, 'Incoming Answered (%)'] = 0.0
        test_output[row, 'Incoming Lost (%)'] = 1 - test_output[row, 'Incoming Answered (%)']  # Lazy percentage

        try:
            test_output[row, 'Average Incoming Duration'] = str(
                test_output[row, 'Average Incoming Duration'] / test_output[
                    row, 'I/C Answered']
            )
        except ZeroDivisionError:
            test_output[row, 'Average Incoming Duration'] = '0:00:00'

        try:
            test_output[row, 'Average Wait Answered'] = str(
                test_output[row, 'Average Wait Answered'] / test_output[
                    row, 'I/C Answered']
            )
        except ZeroDivisionError:
            test_output[row, 'Average Wait Answered'] = '0:00:00'

        try:
            test_output[row, 'Average Wait Lost'] = str(
                test_output[row, 'Average Wait Lost'] / test_output[
                    row, 'I/C Lost']
            )
        except ZeroDivisionError:
            test_output[row, 'Average Wait Lost'] = '0:00:00'

        test_output[row, 'Longest Waiting Answered'] = str(test_output[row, 'Longest Waiting Answered'])

        try:
            test_output[row, 'PCA'] = (
                (test_output[row, 'Calls Ans Within 15'] + test_output[row, 'Calls Ans Within 30']) /
                test_output[row, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row, 'PCA'] = 0.0

    # print(test_output)


if __name__ == '__main__':
    main()
