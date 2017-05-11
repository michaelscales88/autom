from sqlalchemy import Column, DateTime


from automated_sla_tool.src.flexible_storage import FlexibleStorage


class SlaStorage(FlexibleStorage):

    __tablename__ = 'sla_storage'

    start = Column('start_time', DateTime(timezone=True), nullable=False)
    end = Column('end_time', DateTime(timezone=True), nullable=False)

