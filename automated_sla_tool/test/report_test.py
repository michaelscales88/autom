from datetime import datetime, timedelta
import datetime as dt
from pyexcel import Sheet
from collections import OrderedDict
from json import dumps

from automated_sla_tool.test.PG_json_test import session_data
from automated_sla_tool.test.flexible_storage import MyEncoder
from automated_sla_tool.src.app_settings import AppSettings


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
        # 'Longest Waiting Answered',
        # 'PCA'
    ]

    settings = AppSettings(file_name=_settings)
    test_output = Sheet(
        colnames=output_headers
    )
    records = session_data(datetime.today().date().replace(year=2017, month=5, day=1))

    for client_num in settings['Clients']:
        additional_row = OrderedDict(
            # [
            #     (client_num, [0] * len(output_headers))     # All zeroes to start
            # ]
            [
                (client_num,
                 [0, 0, 0, 0, 0, 0, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0, 0, 0]
                 )
            ]
        )
        test_output.extend_rows(additional_row)

    # Update output from data source
    for record in records:
        call_group = str(record.data['Call Group'])
        client_data = settings['Clients'].get(call_group, None)  # Determine if this is a valid client/track 24 hr cli
        call_duration = record.data['End Time'] - record.data['Start Time']
        wait_duration = call_duration - record.data['Talking Duration']
        if client_data and (record.start.time() > dt.time()):
            print(dumps(record.data, cls=MyEncoder))
            if record.data['Answered']:
                # Do answered work
                test_output[call_group, 'I/C Answered'] += 1
                test_output[call_group, 'I/C Presented'] += 1
                test_output[call_group, 'Average Incoming Duration'] += record.data['Talking Duration']
                test_output[call_group, 'Average Wait Answered'] += wait_duration
                if call_group == '7521':
                    print('SWS duration', record.id, wait_duration)

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    test_output[call_group, 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    test_output[call_group, 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    test_output[call_group, 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    test_output[call_group, 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    test_output[call_group, 'Calls Ans Within 999'] += 1

                else:
                    test_output[call_group, 'Call Ans + 999'] += 1

            else:
                # Do lost work
                if record.data['Voicemail'] and record.data['Voicemail'] > timedelta(seconds=20):
                    test_output[call_group, 'Voice Mails'] += 1
                    test_output[call_group, 'I/C Presented'] += 1

                elif (record.data['End Time'] - record.data['Start Time']) > timedelta(seconds=20):
                    test_output[call_group, 'I/C Lost'] += 1
                    test_output[call_group, 'I/C Presented'] += 1
                    test_output[call_group, 'Average Wait Lost'] += call_duration

                else:
                    print('didnt count')

    # Update programmatic columns
    for row in test_output.rownames:
        try:
            test_output[row, 'Incoming Answered (%)'] = test_output[row, 'I/C Answered'] / test_output[
                row, 'I/C Presented']
        except ZeroDivisionError:
            test_output[row, 'Incoming Answered (%)'] = 0.0
        test_output[row, 'Incoming Lost (%)'] = 1 - test_output[row, 'Incoming Answered (%)']   # Lazy percentage

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

        # Calculated percentage
        # test_output[row, 'Incoming Lost (%)'] = (
        #         test_output[row, 'I/C Lost'] + test_output[row, 'Voice Mails']
        # ) / test_output[row, 'I/C Presented']

    print(test_output)

if __name__ == '__main__':
    main()
