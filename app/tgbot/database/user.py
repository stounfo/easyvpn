from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship

from database.base_sqlalchemy_model import BaseSQLAlchemyModel


class User(BaseSQLAlchemyModel):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)

    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

