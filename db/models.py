from db.settings import engine, Base
from sqlalchemy import Column, String, PickleType, Sequence
from sqlalchemy.types import DateTime, Integer
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta

# store the last conversation history
class Chat(Base):
    id =  Column(Integer, Sequence('chat_table_seq', start=1), primary_key=True)
    chat_id = Column(String(length=255), nullable=True)
    email = Column(String(length=255), index=True)
    user_id = Column(String(length=255))
    content = Column(PickleType)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone(timedelta(hours=+9), 'JST')))

    __tablename__ = "chat"
    __table_args__ = {"extend_existing": True}

class ChatHistory(Base):
    id =  Column(Integer, Sequence('chat_table_seq', start=1), primary_key=True)
    chat_id = Column(String(length=255), index=True)
    email = Column(String(length=255), index=True)
    user_id = Column(String(length=255))
    content = Column(PickleType)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __tablename__ = "chat_history"
    __table_args__ = {"extend_existing": True}

Base.metadata.create_all(bind=engine, checkfirst=True)

