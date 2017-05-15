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
        cached_data = grouped_records.get(
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
        if not cached_data['Call Group']:
            cached_data['Call Group'] = record['dialed_party_number']

        # Get calling party and receiving party from the 'Ringing' row
        if record['event_type'] == 1:
            cached_data['Calling Party'] = record['calling_party']
            cached_data['Receiving Party'] = record['receiving_party']

        # Talking Duration
        if record['event_type'] == 4:
            cached_data['Talking Duration'] += (record['end_time'] - record['start_time'])

        # Voicemail event: store timedelta for later comparison
        if record['event_type'] == 10:
            print('checking a voicemail', key, record['end_time'] - record['start_time'])
            cached_data['Voicemail'] = record['end_time'] - record['start_time']

        # MIN start time
        if not cached_data['Start Time']:   # Set if none
            cached_data['Start Time'] = record['start_time']
        elif cached_data['Start Time'] > record['start_time']:  # or with a new lowest start_time
            cached_data['Start Time'] = record['start_time']

        # MAX end time
        if not cached_data['End Time']:     # Set if none
            cached_data['End Time'] = record['end_time']
        elif cached_data['End Time'] < record['end_time']:      # or with a new highest end_time
            cached_data['End Time'] = record['end_time']

        # An answered call has talking time
        if (
            not cached_data['Answered']
            and cached_data['Talking Duration'] > timedelta(0)
        ):
            cached_data['Answered'] = True

        # DO WORK
        grouped_records[key] = cached_data
    return grouped_records


if __name__ == '__main__':
    test(query_date='2017-05-01')
