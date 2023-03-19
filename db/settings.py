from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///chat.sqlite3", echo=False)
session = sessionmaker(bind=engine)()

Base = declarative_base()
Base.metadata.create_all(bind=engine, checkfirst=True)
