import os, csv, pandas as pd
from pdb import set_trace
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from util import table_exists, sql, add_var, modify_var

import connect_database

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

database_url = os.environ.get('DATABASE_URL', -1)
if database_url == -1:
    database_url == config['DEFAULT']['database url']

db = connect_database.get_db(database_url=database_url)

# Check table existence, decide what to rebuild
tables = {}
tables['db config'] = table_exists(config['db config table'], db)
tables['books'] = table_exists(config['books table'], db)
tables['users'] = table_exists(config['users table'], db)
tables['reviews'] = table_exists(config['reviews table'], db)

if not tables['db config']:
    config['overwrite']['db_config_modify'] = "True"
if not tables['books']:
    config['overwrite']['books_table_modify'] = "True"
    config['DEFAULT']['import books'] = "True"
if not tables['users']: config['overwrite']['user_table_modify'] = "True"
if not tables['reviews']: config['overwrite']['reviews_table_modify'] = "True"

# Creating tables one by one
# db config
if config['recreate']['db config'] == "True":
    sql(config['queries']['db config'], db=db)
    for key in config['overwrite'].keys()
        add_var(key, config['overwrite'][key], db=db)
for key in config['overwrite'].keys()
    modify_var(key, config['overwrite'][key], db=db)

# books
if config['overwrite']['books_table_modify'] == "True":
    if tables['books']:
        sql(config['queries']['drop books'], rollback=True)
    sql(config['queries']['create books'], db=db)

if config['overwrite']['books_table_modify'] == 'True' or config['DEFAULTS']['import books'] == 'True':
    sql(config['queries']['clear books'])
