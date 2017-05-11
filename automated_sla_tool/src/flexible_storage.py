from datetime import datetime
from sqlalchemy import (
    Column, Integer, String,
    TypeDecorator, DateTime
)
from sqlalchemy.ext import mutable, declarative
from json import loads, dumps

from automated_sla_tool.src.report_utilities import ReportUtilities


class JsonEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = String

    def process_bind_param(self, value, dialect):
        return dumps(value, default=ReportUtilities.datetime_handler)

    def process_result_value(self, value, dialect):
        return loads(value, object_hook=ReportUtilities.datetime_handler)


@declarative.as_declarative()
class FlexibleStorage(object):

    __tablename__ = 'flexible_storage'

    id = Column('id', Integer, primary_key=True)
    data = Column('json_data', JsonEncodedDict)
    created_on = Column('created_on', DateTime(), default=datetime.now)
    updated_on = Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, mutable_json=False):
        if mutable_json:
            mutable.MutableDict.associate_with(JsonEncodedDict)  # Toggle this to make the JSON data mutable

    @property
    def columns(self):
        """Return the value in the column, or the data type if no value is set"""
        return [(p.key, getattr(self, p.key) if getattr(self, p.key) else p.columns[0].type)
                for p in [self.__mapper__.get_property_by_column(c) for c in self.__mapper__.columns]]

    def __repr__(self):
        return "{table_name} ({columns})".format(
            table_name=self.__tablename__ if self.__tablename__ else self.__class__.__name__,
            columns=', '.join(['{0}={1!r}'.format(*_) for _ in self.columns])
        )
