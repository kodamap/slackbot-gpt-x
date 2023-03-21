from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///chat.db", echo=False)
session = sessionmaker(bind=engine)()
Base = declarative_base()
