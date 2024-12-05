# common/db/models/base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Base class for all models
Base = declarative_base()

def init_db(engine_url="mysql+pymysql://root:tolga1194031@35.184.196.46/blushyv2" ):
    """
    Initializes the database connection and returns a sessionmaker instance.
    
    :param engine_url: The database URL.
    :return: Sessionmaker instance.
    """
    engine = create_engine(engine_url,
                           poolclass=QueuePool,
                            pool_size=20,  # Increase base pool size
                            max_overflow=30,  # Increase maximum overflow connections
                            pool_timeout=60,  # Increase timeout (in seconds)
                            pool_recycle=3600  # Recycle connections after 1 hour
                            )
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)