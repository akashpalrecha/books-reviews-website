from flask import Flask, session, escape, url_for, render_template, request, redirect
from cerberus import Validator
from util import make_link, make_lines, sql, get_password, search_in_books
import connect_database
db = connect_database.get_db()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if connect_database.config['overwrite']['setup again'] == "True":
    import setup

db = connect_database.get_db()

@app.route('/')
def index():
    return make_lines(['login', 'register', 'register_error', 'home_books'])


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

@app.route('/random_page')
def random_page():
    return render_template('search_results.html',
                           nav_1="Logout", nav_1_link="logout",
                           nav_2="Search", nav_2_link="home_books")