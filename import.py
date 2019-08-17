import os, pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# Good progress bars
try :
    __IPYTHON__
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm as tqdm

# -------- SETTING UP --------
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("Careful here, DATABASE_URL system var not set!")
    database_url = 'postgresql://akash:Extremus2.0@localhost:5432/first'

engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind=engine))

data_path = 'books.csv'
data = pd.read_csv(data_path)

create_table_query = """CREATE TABLE books (
           isbn VARCHAR UNIQUE NOT NULL,
           title VARCHAR NOT NULL,
           author VARCHAR,
           year INTEGER);"""

drop_table_query = """DROP TABLE books"""

get_table_query = """SELECT table_name
FROM information_schema.tables
WHERE table_type='BASE TABLE'
AND table_schema='public';"""

# Create table
db.rollback()
tables = db.execute(get_table_query).fetchall()
if 'books' in list(tables[0]):
    db.execute(drop_table_query)
db.execute(create_table_query)
db.commit()

# -------- SETUP DONE --------

def escape_sql_characters(q):
    new = ''
    q = str(q)
    for c in q:
        if c == "'":
            new += "''"
        else:
            new += c
    return new

def escape_list(queries):
    if type(queries) != list:
        return escape_sql_characters(queries)
    else:
        new = []
        for q in queries:
            new.append(escape_sql_characters(q))
        return new


db.rollback()
for i in tqdm(range(len(data))):
    book = data.iloc[i]
    isbn, title, author, year = escape_list(list(book))
#     set_trace()
    query = f"INSERT INTO books(isbn, title, author, year)" + \
           f""" VALUES ('{isbn}', '{title}', '{author}', '{year}')"""
    db.execute(query)

db.commit()

print("Successful")