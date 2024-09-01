# common/db/session.py

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from blushy.db.models import base

DATABASE_URL="mysql+pymysql://root:tolga1194031@35.184.196.46/blushydb"
# Create engine and session
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_session():
    """
    Returns a new session object.
    
    :return: SQLAlchemy session object.
    """
    session = Session()
    if not session or not session.is_active:
        base.init_db()
        session = Session()
    return session