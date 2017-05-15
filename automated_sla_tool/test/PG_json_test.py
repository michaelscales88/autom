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
        call_data = SlaStorage(
            id=call_id,
            start=call_data_dict['Start Time'],
            end=call_data_dict['End Time'],
            data=call_data_dict
        )
        session.add(call_data)
    session.commit()

    # for row in session.query(SlaStorage).all():
    #     print(row)

    for row in session.query(SlaStorage).filter(func.date(session_date)).all():
        yield row
    #
    # # Verify the PK doesn't break the insert if the news records preceed the lowest id in the db
    # for call_id, call_data_dict in test(query_date='2017-04-28').items():   # Get data from PG connection
    #     session.add(
    #         SlaStorage(
    #             id=call_id,
    #             data=call_data_dict
    #         )
    #     )
    # session.commit()
    #
    # for row in session.query(SlaStorage).all():
    #     # dumps(row, default=ReportUtilities.datetime_handler)
    #     print(row)


if __name__ == '__main__':
    session_data()
