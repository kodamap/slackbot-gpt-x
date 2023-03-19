from sqlalchemy import create_engine
from sqlalchemy import Column, String, PickleType
from sqlalchemy.ext.mutable import MutableList
from db.settings import engine, Base


class Chat(Base):
    user = Column(String(length=255), primary_key=True)
    chat = Column(MutableList.as_mutable(PickleType))

    __tablename__ = "chat_history"
    __table_args__ = {"extend_existing": True}


Base.metadata.create_all(bind=engine)
