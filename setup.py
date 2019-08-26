import os
from util import table_exists, sql, add_var, modify_var, populate_books_table
import connect_database

config = connect_database.config

database_url = os.environ.get('DATABASE_URL', -1)
if database_url == -1:
    database_url = config['DEFAULT']['database url']

db = connect_database.get_db(database_url=database_url)
print("Database connected.")
# Check table existence, decide what to rebuild
tables = {}
tables['db config'] = table_exists(config['DEFAULT']['db config table'], db)
tables['books'] = table_exists(config['DEFAULT']['books table'], db)
tables['users'] = table_exists(config['DEFAULT']['users table'], db)
tables['reviews'] = table_exists(config['DEFAULT']['reviews table'], db)
print(tables)

if not tables['db config']:
    config['overwrite']['db_config_modify'] = "True"
if not tables['books']:
    config['overwrite']['books_table_modify'] = "True"
    config['DEFAULT']['import books'] = "True"
if not tables['users']: config['overwrite']['user_table_modify'] = "True"
if not tables['reviews']: config['overwrite']['reviews_table_modify'] = "True"

print(dict(config['overwrite']))
print("Decisions made.\nWorking on:")
# Creating tables one by one
# db config
print("DB Config table.")
if config['overwrite']['db_config_modify'] == "True":
    if tables['db config']:
        sql(config['queries']['drop db config'], db=db, rollback=True)
    sql(config['queries']['db config'], db=db)
    for key in config['overwrite'].keys():
        add_var(key, config['overwrite'][key], db=db)
for key in config['overwrite'].keys():
    modify_var(key, config['overwrite'][key], db=db)

# Books
print("Books table.")
if config['overwrite']['books_table_modify'] == "True":
    if tables['books']:
        sql(config['queries']['drop books'], rollback=True)
    sql(config['queries']['create books'], db=db)

if config['overwrite']['books_table_modify'] == 'True' or config['DEFAULT']['import books'] == 'True':
    sql(config['queries']['clear books'])
    populate_books_table(db=db)

# Users
print("Users table.")
if config['overwrite']['user_table_modify'] == 'True':
    if tables['users']:
        sql(config['queries']['drop users'], rollback=True)
    sql(config['queries']['create users'], db=db)

# Reviews
print("Reviews table.")
if config['overwrite']['reviews_table_modify'] == 'True':
    if tables['reviews']:
        sql(config['queries']['drop reviews'], rollback=True)
    sql(config['queries']['create reviews'], db=db)

# Rewrite Config.ini
print("Finishing up.")
config['overwrite']['setup again'] = "False"
config.write(open('config.ini', mode='w'))
print("Done.")