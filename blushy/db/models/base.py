# common/db/models/base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Base class for all models
Base = declarative_base()

def init_db(engine_url="mysql+pymysql://root:tolga1194031@35.184.196.46/blushyv2" ):
    """
    Initializes the database connection and returns a sessionmaker instance.
    
    :param engine_url: The database URL.
    :return: Sessionmaker instance.
    """
    engine = create_engine(engine_url,
                           pool_size=20,  # Increase from 5
                            max_overflow=30,  # Increase from 10
                            pool_timeout=60,  # Increase timeout from 30
                            pool_pre_ping=True  # Add connection health check)
                            )
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)