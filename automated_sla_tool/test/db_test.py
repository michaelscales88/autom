from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import defaultdict

from automated_sla_tool.src.data_center import DataCenter


def test(query_date):
    pk = 'call_id'
    engine = create_engine('postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall')

    dc = DataCenter()
    meta = MetaData()
    Session = sessionmaker(bind=engine)
    meta.reflect(bind=engine)
    session = Session()

    statement = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''.format(date=str(query_date))

    start = datetime.now()
    print('Start:', start)
    result = session.execute(statement)
    list_of_records = [dict(zip(row.keys(), row)) for row in result]

    for table in reversed(meta.sorted_tables):
        print(table)
    stop = datetime.now()
    print('Stop:', stop)
    print('Total:', stop - start)

    grouped_records = {}
    for record in list_of_records:
        key = record.pop(pk)
        call_data = grouped_records.get(
            key,
            {   # This could be a configobj from AppSettings "Call Template"
                'Answered': False,                  # Answered occurs in the call ID
                'Talking Duration': timedelta(0),
                'Start Time': None,                 # MIN time
                'End Time': None,                   # MAX time
                'Voicemail': False,                 # This needs a time check as well
                'Calling Party': None,              # Calling Party @ "ringing" event
                'Receiving Party': None,            # Receiving Party @ "ringing" event
                'Call Group': None                  # Hunt Group from c_call table
            }
        )

        # Hunt Group
        if not call_data['Call Group']:
            call_data['Call Group'] = record['dialed_party_number']

        # Get calling party and receiving party from the 'Ringing' row
        if record['event_type'] == 1:
            call_data['Calling Party'] = record['calling_party']
            call_data['Receiving Party'] = record['receiving_party']

        # Talking Duration
        if record['event_type'] == 4:
            call_data['Talking Duration'] += (record['end_time'] - record['start_time'])

        # Voicemail event: store timedelta for later comparison
        if record['event_type'] == 10:
            print('checking a voicemail', key, record['end_time'] - record['start_time'])
            call_data['Voicemail'] = record['end_time'] - record['start_time']

        # MIN start time
        if call_data['Start Time'] and call_data['Start Time'] > record['start_time']:
            call_data['Start Time'] = record['start_time']
        else:
            call_data['Start Time'] = record['start_time']

        # MAX end time
        if call_data['End Time'] and call_data['End Time'] < record['end_time']:
            call_data['End Time'] = record['end_time']
        else:
            call_data['End Time'] = record['end_time']

        # An answered call has talking time
        if (
            not call_data['Answered']
            and call_data['Talking Duration'] > timedelta(0)
        ):
            call_data['Answered'] = True

        # DO WORK
        grouped_records[key] = call_data
    return grouped_records


if __name__ == '__main__':
    test(query_date='2017-05-01')
