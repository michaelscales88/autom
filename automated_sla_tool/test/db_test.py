from datetime import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import defaultdict


from automated_sla_tool.src.DataCenter import DataCenter


def test():
    pk = 'call_id'
    engine = create_engine('postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall')

    dc = DataCenter()
    meta = MetaData()
    Session = sessionmaker(bind=engine)

    meta.reflect(bind=engine)
    session = Session()
    statement = '''
    Select Distinct c_call.call_id, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '2017-05-01' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''
    start = datetime.now()
    print('Start:', start)
    result = session.execute(statement)
    list_of_records = [dict(zip(row.keys(), row)) for row in result]
    dc.print_record(list_of_records)
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
            0
        )
        call_data += 1
        # DO WORK
        grouped_records[key] = call_data
    dc.print_record(grouped_records)
    # grouped_records = defaultdict(list)
    # for record in list_of_records:
    #     key = record.pop('call_id')
    #     grouped_records[key].append(record)
    # print('grouped records')
    # dc.print_record(grouped_records)
    #
    # print('Compiling records')
    # for record, record_data in grouped_records.items():
    #     print(record)
    #     for rd in record_data:
    #         print(rd['event_type'])

if __name__ == '__main__':
    test()
