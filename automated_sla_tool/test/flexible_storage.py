from datetime import datetime, timedelta
from sqlalchemy import (
    Column, Integer, String,
    TypeDecorator, DateTime
)
from decimal import Decimal
from dateutil import parser
from sqlalchemy.ext import mutable
from sqlalchemy.ext.declarative import declarative_base
from json import loads, dumps, JSONEncoder


from automated_sla_tool.src.report_utilities import ReportUtilities


Base = declarative_base()


CONVERTERS = {
    'datetime': parser.parse,
    'decimal': Decimal,
    'timedelta': ReportUtilities.to_td
}


class MyEncoder(JSONEncoder):
    """Convert non-serializable data into a value which we can store in our dB"""
    def default(self, obj):
        if isinstance(obj, (datetime,)):
            return {"val": obj.isoformat(), "_spec_type": "datetime"}
        elif isinstance(obj, (Decimal,)):
            return {"val": str(obj), "_spec_type": "decimal"}
        elif isinstance(obj, (timedelta,)):
            return {"val": str(obj), "_spec_type": "timedelta"}
        else:
            return super().default(obj)


def object_hook(obj):
    """Convert json data from its serialized value"""
    _spec_type = obj.get('_spec_type')
    if not _spec_type:
        return obj

    if _spec_type in CONVERTERS:
        return CONVERTERS[_spec_type](obj['val'])
    else:
        raise Exception('Unknown {}'.format(_spec_type))


class JsonEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = String

    def process_bind_param(self, value, dialect):
        return dumps(value, cls=MyEncoder)

    def process_result_value(self, value, dialect):
        return loads(value, object_hook=object_hook)


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
    start = Column('start_time', DateTime(timezone=True))
    end = Column('end_time', DateTime(timezone=True))

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
    start = Column('start_time', DateTime(timezone=True))
    end = Column('end_time', DateTime(timezone=True))
    unique_id1 = Column('receiving_party', Integer)
    unique_id2 = Column('calling_party', Integer)

    __mapper_args__ = {
        'concrete': True
    }


# TODO http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html?highlight=mapper#sqlalchemy.ext.declarative.declarative_base.params.mapper
# this will be a polymorphic base system before I implement... do it friday
