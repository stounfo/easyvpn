from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL, SQL_ECHO

Base = declarative_base()
metadata = Base.metadata
engine_sync = create_engine(DATABASE_URL, echo=SQL_ECHO, connect_args={'timeout': 3})
sync_session_factory = sessionmaker(bind=engine_sync,
                                    autocommit=False)


@contextmanager
def get_session():
    session = sync_session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
