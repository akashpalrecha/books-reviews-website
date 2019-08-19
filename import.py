import pandas as pd
from util import table_exists, sql, escape_list
import connect_database
# Good progress bars
try:
    __IPYTHON__
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm as tqdm


def populate_books_table(db, data_path='books.csv'):
    if not table_exists('books', db=db):
        sql(connect_database.config['queries']['create books'], rollback=True, db=db)
    sql(connect_database.config['queries']['clear books'], rollback=True)
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


if __name__ == '__main__':
    db = connect_database.get_db()
    populate_books_table(db=db)
