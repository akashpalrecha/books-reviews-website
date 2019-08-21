import connect_database
from util import populate_books_table

db = connect_database.get_db()
populate_books_table(db=db)