# common/db/session.py
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine,text
from blushy.db.models import base
from sqlalchemy.exc import OperationalError
import time



from sqlalchemy.exc import OperationalError, PendingRollbackError
import time

def get_session(max_retries=3, retry_delay=1):
    """
    Returns a new session object with retry mechanism.
    
    :param max_retries: Maximum number of connection attempts.
    :param retry_delay: Delay in seconds between retries.
    :return: SQLAlchemy session object.
    """
    global Session
    try:
        session = Session()
        print("session is valid")
    except Exception as e:
        Session = base.init_db()
        session = Session()
        print("session created")

    
    for attempt in range(max_retries):
        try:
            
            
            # Test the connection
            session.execute(text("SELECT 1"))
            
            return session
        except PendingRollbackError:
            # If there's a pending rollback, perform it and try again
            if session:
                session.rollback()
            continue
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts.")
                raise e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            if session:
                session.rollback()
            raise

    raise Exception("Failed to establish a database connection.")

