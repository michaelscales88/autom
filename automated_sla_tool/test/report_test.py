from datetime import datetime, timedelta, time
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

test_client = 7523


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def match(record_list, match_val=None):
    matched_records = []

    # print(
    #     'Matching to',
    #     getattr(match_record, 'id'),
    #     getattr(match_record, 'unique_id2'),
    #     getattr(match_record, 'unique_id1')
    # )
    for record in record_list:
        # print('Comparing', getattr(record, 'id'))
        match0 = (
            getattr(match_val, 'data')['Event Summary'].get('4', timedelta(0))
            == getattr(record, 'data')['Event Summary'].get('4', timedelta(0))
            == timedelta(0)
        )
        # print(
        #     match0,
        #     getattr(match_val, 'data')['Event Summary'].get('4', timedelta(0)),
        #     getattr(record, 'data')['Event Summary'].get('4', timedelta(0))
        # )

        match1 = getattr(match_val, 'unique_id2') == getattr(record, 'unique_id2')
        # print(match1, getattr(record, 'unique_id2'))

        match2 = getattr(match_val, 'unique_id1') == getattr(record, 'unique_id1')
        # print(match2, getattr(record, 'unique_id1'))

        match3 = (getattr(record, 'start') - getattr(match_val, 'end')) < timedelta(seconds=61)
        # print(match3, getattr(record, 'start') - getattr(match_record, 'end'))

        all_matched = all(
            [
                match0,
                match1,
                match2,
                match3
            ]
        )

        # print(all_matched)

        if all_matched:
            # print('Perform match behavior', getattr(record, 'id'))
            matched_records.append(getattr(record, 'id'))

    return matched_records


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

    for client_num in (*settings['Clients'], 'Summary'):
        additional_row = OrderedDict(
            [
                (client_num,
                 [0, 0, 0, 0, 0, 0, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0, 0, 0, timedelta(0), 0]
                 )
            ]
        )
        test_output.extend_rows(additional_row)

    records = session_data(datetime.today().date().replace(year=2017, month=5, day=17))

    # Filter Step
    try:
        for x in range(0, len(records)):
            match_record = records[x]
            matches = match(records[x+1:], match_val=match_record)
            if (
                    len(matches) > 1
                    and (match_record.end - match_record.start > timedelta(seconds=20))
                    and match_record.data['Event Summary'].get('10', timedelta(0)) == timedelta(0)
            ):
                # print('Matched value:', match_record)
                for a_match in matches:
                    # if a_match == 1497228:
                    #     print(match_record.id, matches)
                    for i, o in enumerate(records):
                        if getattr(o, 'id') == a_match:
                            del records[i]
                            # print('Removed', a_match, 'at', i)
                            break

    except IndexError:
        # x has moved past the end of the list of remaining records
        pass

    # Process Step
    for record in records:
        row_name = str(record.unique_id1)    # This is how we bind our client settings
        if row_name in test_output.rownames and time(hour=7) <= record.start.time() <= time(hour=19):
            call_duration = record.end - record.start
            talking_time = record.data['Event Summary'].get('4', timedelta(0))
            voicemail_time = record.data['Event Summary'].get('10', timedelta(0))
            hold_time = sum(
                [record.data['Event Summary'].get(event_type, timedelta(0)) for event_type in ('5', '6', '7')],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time
            # DO the rest of the output work
            if talking_time > timedelta(0):
                if record.unique_id1 == test_client:
                    print('I am an answered call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Answered'] += 1
                test_output[row_name, 'Average Incoming Duration'] += talking_time
                test_output[row_name, 'Average Wait Answered'] += wait_duration

                # Adding to Summary
                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Answered'] += 1
                test_output['Summary', 'Average Incoming Duration'] += talking_time
                test_output['Summary', 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    test_output[row_name, 'Calls Ans Within 15'] += 1
                    test_output['Summary', 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    test_output[row_name, 'Calls Ans Within 30'] += 1
                    test_output['Summary', 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    test_output[row_name, 'Calls Ans Within 45'] += 1
                    test_output['Summary', 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    test_output[row_name, 'Calls Ans Within 60'] += 1
                    test_output['Summary', 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    test_output[row_name, 'Calls Ans Within 999'] += 1
                    test_output['Summary', 'Calls Ans Within 999'] += 1

                else:
                    test_output[row_name, 'Call Ans + 999'] += 1
                    test_output['Summary', 'Call Ans + 999'] += 1

                if wait_duration > test_output[row_name, 'Longest Waiting Answered']:
                    test_output[row_name, 'Longest Waiting Answered'] = wait_duration

                if wait_duration > test_output['Summary', 'Longest Waiting Answered']:
                    test_output['Summary', 'Longest Waiting Answered'] = wait_duration

            elif voicemail_time > timedelta(seconds=20):
                if record.unique_id1 == test_client:
                    print('I am a voice mail call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'Voice Mails'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'Voice Mails'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            elif call_duration > timedelta(seconds=20):
                if record.unique_id1 == test_client:
                    print('I am a lost call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Lost'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Lost'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            else:
                pass

    # Finalize step
    for row in test_output.rownames:
        try:
            test_output[row, 'Incoming Answered (%)'] = '{0:.1%}'.format(
                test_output[row, 'I/C Answered'] / test_output[row, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row, 'Incoming Answered (%)'] = 1.0

        try:
            test_output[row, 'Incoming Lost (%)'] = '{0:.1%}'.format(
                (test_output[row, 'I/C Lost'] + test_output[row, 'I/C Lost'])
                / test_output[row, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row, 'Incoming Lost (%)'] = 0.0

        try:
            test_output[row, 'Average Incoming Duration'] = str(
                chop_microseconds(test_output[row, 'Average Incoming Duration'] / test_output[row, 'I/C Answered'])
            )
        except ZeroDivisionError:
            test_output[row, 'Average Incoming Duration'] = '0:00:00'

        try:
            test_output[row, 'Average Wait Answered'] = str(
                chop_microseconds(test_output[row, 'Average Wait Answered'] / test_output[row, 'I/C Answered'])
            )
        except ZeroDivisionError:
            test_output[row, 'Average Wait Answered'] = '0:00:00'

        try:
            test_output[row, 'Average Wait Lost'] = str(
                chop_microseconds(test_output[row, 'Average Wait Lost'] / test_output[row, 'I/C Lost'])
            )
        except ZeroDivisionError:
            test_output[row, 'Average Wait Lost'] = '0:00:00'

        test_output[row, 'Longest Waiting Answered'] = str(
            chop_microseconds(test_output[row, 'Longest Waiting Answered'])
        )

        try:
            test_output[row, 'PCA'] = '{0:.1%}'.format(
                (test_output[row, 'Calls Ans Within 15'] + test_output[row, 'Calls Ans Within 30'])
                / test_output[row, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row, 'PCA'] = 0.0

    print(test_output)


if __name__ == '__main__':
    main()
