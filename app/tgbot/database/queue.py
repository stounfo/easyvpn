from datetime import datetime

from sqlalchemy import Column, Integer, Text, String, DateTime

from database.base_sqlalchemy_model import BaseSQLAlchemyModel


class Queue(BaseSQLAlchemyModel):
    __tablename__ = "queues"
    id = Column(Integer, primary_key=True, index=True)
    payload = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="created", nullable=False)  # created / completed
    completed = Column(DateTime)
