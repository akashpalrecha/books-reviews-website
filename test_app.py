from flask import Flask, session, escape, url_for, render_template, request, redirect
from cerberus import Validator
from util import make_link, make_lines
import connect_database

app = Flask(__name__)

if connect_database.config['overwrite']['setup again'] == "True":
    import setup

db = connect_database.get_db()

@app.route('/')
def index():
    return make_lines(['login', 'register', 'register_error'])


@app.route('/login')
def login():
    return render_template('login.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register")


@app.route('/register')
def register():
    return render_template('register.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register")


@app.route('/process_register', methods=["POST"])
def process_register():
    email = request.form.get("email")
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
    return render_template('register_error.html',
                           nav_1="Login", nav_1_link="login",
                           nav_2="Register", nav_2_link="register",
                           error_message=error_message)