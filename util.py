"""
Contains helper functions for the web app.
"""
from sqlalchemy.orm import scoped_session
from pathlib import Path
import connect_database
import requests
db = connect_database.get_db()

def make_lines(lines: list, link=True):
    """ returns HTML code that separates all lines by <br> """
    if type(lines) != list:
        if link:
            return make_link(lines)
        return lines
    else:
        response = ""
        for line in lines:
            if link:
                line = make_link(line)
            response += str(line) + "<br>"
        return response


def make_link(line):
    """ Returns HTML for 'line' rendered as a LINK"""
    return f"<a href='{line}'>{line}</a>"


def add_user(email:str, password:str, db:scoped_session):
    """ Adds a USER to the Database """
    query = ""
    db.execute()


def sql(query, db:scoped_session=db, fetch=False, rollback=False):
    """ runs sql query on db """
    if rollback: db.rollback()
    if fetch:
        return db.execute(query).fetchall()
    db.execute(query)
    db.commit()


def table_exists(table:str, db:scoped_session=db):
    """ checks if table exists in db """
    get_table_query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_type='BASE TABLE'
    AND table_schema='public';
    """
    res = sql(get_table_query, fetch=True, db=db)
    res = [list(o) for o in res]
    return table in sum(res, [])


def add_var(var, value, db:scoped_session=db, rollback=False, table="db_config"):
    """ adds a new variable in table in db """
    query = f"INSERT INTO {table} (var, value) VALUES ('{var}', '{value}')"
    sql(query, rollback=rollback, db=db)


def del_var(var, db:scoped_session=db, rollback=False, table="db_config"):
    """ delets variable in table in db """
    query = f"DELETE FROM {table} WHERE var = '{var}'"
    sql(query, rollback=rollback, db=db)


def modify_var(var, value, db:scoped_session=db, rollback=False, table="db_config"):
    """ updates variable in table in db """
    query = f"UPDATE {table} SET value = '{value}' WHERE var = '{var}'"
    sql(query, rollback=rollback, db=db)


def get_var(var, db:scoped_session=db, rollback=False, table="db_config"):
    """ gets variable from table in db """
    query = f"SELECT value FROM {table} WHERE var = '{var}'"
    res = sql(query, fetch=True, rollback=rollback, db=db)
    if len(res) > 0:
        return res[0][0]
    else:
        return res


def exists_var(var, db:scoped_session=db, rollback=False, table="db_config"):
    """ Checks if variable exists in table of db """
    return len(get_var(var, rollback=rollback, db=db, table=table)) > 0


def escape_sql_characters(q):
    """ returns a string with all single quotes converted to double quotes """
    new = ''
    q = str(q)
    for c in q:
        if c == "'": new += "''"
        else: new += c
    return new


def escape_list(queries):
    """ Applies escape_sql_characters to all strings in the list of queries and returns another list """
    if type(queries) != list:
        return escape_sql_characters(queries)
    else:
        new = []
        for q in queries:
            new.append(escape_sql_characters(q))
        return new


def populate_books_table(db:scoped_session=db, data_path='books.csv'):
    # Good progress bars
    try:
        __IPYTHON__
        from tqdm import tqdm_notebook as tqdm
    except NameError:
        from tqdm import tqdm as tqdm

    import pandas as pd
    if not table_exists('books', db=db):
        sql(connect_database.config['queries']['create books'], rollback=True, db=db)
    sql(connect_database.config['queries']['clear books'], rollback=True)

    data_path = Path(data_path).absolute()
    data = pd.read_csv(data_path)
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


def get_password(email, db:scoped_session=db):
    passwd_query = f"SELECT password FROM user_data WHERE email='{email}'"
    password = sql(passwd_query, db=db, rollback=True, fetch=True)
    return password


def search_in_books(search:str, db:scoped_session=db):
    query1 = f"SELECT * FROM books WHERE title LIKE '%{search}%'"
    query2 = f"SELECT * FROM books WHERE isbn LIKE '%{search}%'"
    query3 = f"SELECT * FROM books WHERE author LIKE '%{search}%'"
    r1 = sql(query=query1, db=db, fetch=True, rollback=True)
    r2 = sql(query=query2, db=db, fetch=True, rollback=True)
    r3 = sql(query=query3, db=db, fetch=True, rollback=True)
    res = r1 + r2 + r3
    for i, book in enumerate(res):
        response = get_from_goodreads(book[0])['books'][0]
        book = tuple(book) + (response['reviews_count'], response['average_rating'])
        res[i] = book
    return res



def process_sql_list_result(result:list):
    return [o[0] for o in result]


def get_from_goodreads(isbn:str) -> dict:
    KEY = connect_database.config['DEFAULT']['Goodreads API Key']
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": KEY, "isbns": str(isbn)}).json()
    return res
