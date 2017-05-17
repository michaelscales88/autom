from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from automated_sla_tool.test.db_test import test
from automated_sla_tool.test.flexible_storage import SlaStorage, Base


def session_data(session_date=None):

    if not session_date:
        session_date = datetime.today().date().replace(year=2017, month=5, day=1)

    # Start application
    session_factory = sessionmaker()

    # Set up our sqlite connection
    db = create_engine('sqlite:///:memory:', echo=False)

    Base.metadata.bind = db
    Base.metadata.create_all()  # This creates the table information. Needs to happen before session inst

    # create a configured "Session" class
    # session = scoped_session(Session(bind=db))

    session = session_factory(bind=db)

    # add records from data_src to the local db
    for call_id, call_data_dict in test(query_date=session_date.strftime('%Y-%m-%d')).items(): # Get data from PG connection
        # call_data = SlaStorage(
        #     id=call_id,
        #     start=call_data_dict['Start Time'],
        #     end=call_data_dict['End Time'],
        #     data=call_data_dict
        # )
        call_data = SlaStorage(
            id=call_id,
            start=call_data_dict.pop('Start Time'),
            end=call_data_dict.pop('End Time'),
            unique_id1=call_data_dict.pop('Unique Id1'),
            unique_id2=call_data_dict.pop('Unique Id2'),
            data=call_data_dict
        )
        session.add(call_data)
    session.commit()

    # from json import dumps
    # from automated_sla_tool.test.flexible_storage import MyEncoder
    # for row in session.query(SlaStorage).filter(func.date(session_date)).all():
    #     print(row.id)
    #     print(dumps(row.data['Event Summary'], cls=MyEncoder, indent=4))


    # print(
    #     row.id,
    #     row.data['Talking Duration'],
    #     (row.end - row.start) - row.data['Talking Duration'],   # Wait = Call Duration - Talk Duration - Hold
    #     row.data['Hold Events']                                 # Hold = 'Hold', 'Transfer Hold', 'Park'
    # )

    # for row in session.query(SlaStorage).filter(func.date(session_date)).all():
    #     if row.data["Call Group"] == '7521':
    #         print(row.id)
    #         print(dumps(row.data, cls=MyEncoder, indent=4))
    #
    # for row in session.query(SlaStorage).filter(func.date(session_date)).all():
    #     yield row
    return session.query(SlaStorage).filter(func.date(session_date)).all()


if __name__ == '__main__':
    session_data()
