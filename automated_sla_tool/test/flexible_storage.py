from datetime import datetime
from sqlalchemy import (
    Column, Integer, String,
    TypeDecorator, DateTime
)
from sqlalchemy.ext import mutable
from sqlalchemy.ext.declarative import declarative_base
from json import loads, dumps


from automated_sla_tool.src.report_utilities import ReportUtilities


Base = declarative_base()


class JsonEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = String

    def process_bind_param(self, value, dialect):
        return dumps(value, default=ReportUtilities.datetime_handler)

    def process_result_value(self, value, dialect):
        return loads(value, object_hook=ReportUtilities.datetime_handler)


class FlexibleStorage(Base):
# @declarative.as_declarative() - > won't create tables with the decorator
# class FlexibleStorage(object):
# @as_declarative()
# class Base(object):
#     @declared_attr.cascading
    __tablename__ = 'flexible_storage'

    id = Column('id', Integer, primary_key=True)
    data = Column('json_data', JsonEncodedDict)
    created_on = Column('created_on', DateTime(), default=datetime.now)
    updated_on = Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def mutable():
        mutable.MutableDict.associate_with(JsonEncodedDict)  # Toggle this to make the JSON data mutable

    @property
    def columns(self):
        """Return the value in the column, or the data type if no value is set"""
        return [(p.key, getattr(self, p.key) if getattr(self, p.key) else p.columns[0].type)
                for p in [self.__mapper__.get_property_by_column(c) for c in self.__mapper__.columns]]

    # TODO add some means of putting the pk first
    def __repr__(self):
        """Default representation of table"""
        return "{table_name} ({columns})".format(
            table_name=self.__tablename__ if self.__tablename__ else self.__class__.__name__,
            columns=', '.join(['{0}={1!r}'.format(*_) for _ in self.columns])
        )


class SlaStorage(FlexibleStorage):

    __tablename__ = 'sla_storage'

    id = Column('id', Integer, primary_key=True)
    data = Column('json_data', JsonEncodedDict)
    created_on = Column('created_on', DateTime(), default=datetime.now)
    updated_on = Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    start = Column('start_time', DateTime(timezone=True), nullable=False)
    end = Column('end_time', DateTime(timezone=True), nullable=False)

    __mapper_args__ = {
        'concrete': True
    }


# TODO http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html?highlight=mapper#sqlalchemy.ext.declarative.declarative_base.params.mapper
# this will be a polymorphic base system before I implement... do it friday
