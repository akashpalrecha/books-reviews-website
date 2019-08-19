import pandas as pd
# Good progress bars
try :
    __IPYTHON__
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm as tqdm


def populate_books_tabe(db=db, data_path = 'books.csv'):
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