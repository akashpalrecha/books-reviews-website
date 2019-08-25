from flask import Flask, session, escape, url_for, render_template, request, redirect, jsonify
from flask_session import Session
from cerberus import Validator
from util import sql, get_password, search_in_books, write_review, get_reviews
import connect_database

db = connect_database.get_db()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if connect_database.config['overwrite']['setup again'] == "True":
    print("Setting Up AGAIN.")
    import setup
    print("SETUP OVER")
db = connect_database.get_db()


@app.route('/', methods=['GET'])
def index():
    if session.get('username', -1) != -1:
        return redirect(url_for('home_books'))
    else:
        return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register")


@app.route('/process_login', methods=["POST"])
def process_login():
    email = str(request.form.get("email"))
    passwd= request.form.get("password")
    password = get_password(email, db=db)
    if len(password) == 0:
        message = "Sorry, the email does not exist in our records. Please register."
        return render_template('login_error.html',
                               nav_1="Login", nav_1_link="login",
                               nav_2="Register", nav_2_link="register",
                               message=message)
        pass
    else:
        if passwd == password[0][0]:
            session['username'] = email[:email.rfind('@')]
            return redirect(url_for('home_books'))
            pass
        else:
            message = "The password entered is incorrect. Please try again."
            return render_template('login_error.html',
                                   nav_1="Login", nav_1_link="login",
                                   nav_2="Register", nav_2_link="register",
                                   message=message)
            pass


@app.route('/logout')
def logout():
    session.pop('username', -1)
    return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('register.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register")


@app.route('/process_register', methods=["POST"])
def process_register():
    email = request.form.get("email")
    passwd = get_password(email)
    if len(passwd) > 0:
        return redirect(url_for('register_error', error='already exists'))

    pass1 = request.form.get("pass1")
    pass2 = request.form.get("pass2")

    # validate email
    schema = {'email': {'type': 'string', 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'}}
    document = {'email': email}
    v = Validator(schema)
    if not v.validate(document):
        return redirect(url_for('register_error', error='email'))
    if not pass1 == pass2:
        return redirect(url_for('register_error', error='pass'))

    from util import escape_sql_characters
    email = escape_sql_characters(email)
    pass1 = escape_sql_characters(pass1)
    insert_query = f"INSERT INTO user_data (email, password) VALUES ('{email}','{pass1}')"
    sql(insert_query, db=db, rollback=True)

    return redirect(url_for('register_success'))


@app.route('/register_success')
def register_success():
    message = "Registeration successful. You can now login ;-)"
    return render_template('register_success.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register",
                           message=message)


@app.route('/register_error/<string:error>')
def register_error(error):
    error_message = ''
    if error == 'email':
        error_message = "Please enter a valid email."
    elif error == 'pass':
        error_message = "Passwords do not match."
    elif error == 'already exists':
        error_message = "Sorry. The email already exists in our records. Please register with another email."
    return render_template('register_error.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register",
                           error_message=error_message)


@app.route('/home_books')
def home_books():
    if session.get('username', -1) == -1:
        return escape("Please login to access this page")

    username = session.get('username')
    return render_template('home_books.html',
                           nav_1="Logout", nav_1_link="logout",
                           nav_2="Search", nav_2_link="home_books",
                           username=username)


@app.route('/search_books', methods=['POST'])
def search_books():
    search = request.form.get('search')
    results = search_in_books(search)
    return render_template('search_results.html', results=results,
                           review_count=10, average_score=4,
                           nav_1="Logout", nav_1_link="logout",
                           nav_2="Search", nav_2_link="home_books")


@app.route('/submit_review/<string:isbn>', methods=['POST'])
def submit_review(isbn: str):
    if session.get('username', -1) == -1:
        return escape("Please login to access this page")

    username = session.get('username')
    title = search_in_books(isbn)[0][1]
    review = request.form.get('review')
    rating = request.form.get('book-rating')
    # validate rating:
    if rating not in ['1','2','3','4','5']:
        rating = '1'

    reviews = get_reviews(isbn, db=db)
    users = [tuple(o)[1] for o in reviews]
    if username in users:
        return "You can only review a book once. Please go back to the previous page."
    write_review(isbn, username, title, review, rating, db=db)
    return redirect(url_for('display_book', isbn=isbn))


@app.route('/display_book/<string:isbn>')
def display_book(isbn: str):
    if session.get('username', -1) == -1:
        return escape("Please login to access this page")

    username = session.get('username')
    book = search_in_books(isbn)[0]

    reviews = get_reviews(isbn, db=db)
    return render_template('display_book.html', book=book, reviews=reviews,
                           nav_1="Logout", nav_1_link="logout",
                           nav_2="Search", nav_2_link="home_books")


@app.route('/api/<string:isbn>', methods=["GET"])
def api(isbn:str):
    book = search_in_books(isbn)[0]
    res = {'title': book[1],
           'author': book[2],
           'year': book[3],
           'isbn': book[0],
           'review_count': book[4],
           'average_score': book[5]
           }
    return jsonify(res)


@app.route('/random_page')
def random_page():
    book = ('0380795272', 'Krondor: The Betrayal', 'Raymond E. Feist', '1998', '1434', '4.4')
    return render_template('display_book.html', book=book,
                           nav_1="Logout", nav_1_link="logout",
                           nav_2="Search", nav_2_link="home_books")