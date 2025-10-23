from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.base_sqlalchemy_model import BaseSQLAlchemyModel


class Request(BaseSQLAlchemyModel):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending / approved / rejected
    uuid = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="requests")
