import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

def get_db(database_url=None):
    if not database_url:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("Careful here, DATABASE_URL system var not set!")
            database_url = config['DEFAULT']['database url']

    engine = create_engine(database_url)
    db = scoped_session(sessionmaker(bind=engine))
    return db