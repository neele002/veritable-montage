import os
basedir = os.path.abspath(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(os.environ['DATABASE_URL'], convert_unicode=True)
    #'postgresql://localhost/microblog_dev',convert_unicode=True)
    #os.environ['DATABASE_URL'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from zmodels import User,GameType,Game,TaskUnit,GameTask,GamePlayers,PlayerGameTask 
    Base.metadata.create_all(bind=engine)