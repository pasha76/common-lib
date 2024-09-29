# common/db/session.py

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from blushy.db.models import base
from sqlalchemy.exc import OperationalError
import time

DATABASE_URL="mysql+pymysql://root:tolga1194031@35.184.196.46/blushyv2"
# Create engine and session
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_session(max_retries=3, retry_delay=1):
    """
    Returns a new session object with retry mechanism.
    
    :param max_retries: Maximum number of connection attempts.
    :param retry_delay: Delay in seconds between retries.
    :return: SQLAlchemy session object.
    """
    for attempt in range(max_retries):
        try:
            session = Session()
            if not session or not session.is_active:
                base.init_db()
                session = Session()
            
            # Test the connection
            session.execute("SELECT 1")
            
            return session
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts.")
                raise e

    raise Exception("Failed to establish a database connection.")