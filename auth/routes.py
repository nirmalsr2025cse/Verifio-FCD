from flask import Blueprint , render_template , redirect , url_for , request , session
import bcrypt
from utils.db import FCD_collection
from flask import jsonify
from datetime import date

auth = Blueprint('auth' , __name__)

@auth.route('/')
def index():
    return redirect('/login')


@auth.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')

    user = FCD_collection.find_one({'email': email})

    return jsonify({
        "exists": True if user else False
    })

@auth.route('/check-login', methods=['POST'])
def check_login():
    data = request.get_json()
    if not data:
        return jsonify({'success':False})
    email = data.get('email')
    password = data.get('password')

    email = email.strip()
    password = password.strip()

    user = FCD_collection.find_one({'email': email})

    if not user:
        return jsonify({"success": False, "type": "email"})

    stored_password = user.get('password')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return jsonify({"success": False, "type": "password"})

    session['user'] = email
    return jsonify({"success": True})


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = FCD_collection.find_one({
            'email': email,
        })
        if not user:
            return render_template('index.html', email_error="This account cannot be found.")

        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return render_template('index.html', password_error="Incorrect password")

        if user:
            session['user'] = email
            session.permanent = bool(remember)
            return redirect(url_for('dashboard.home'))
        else:
            return render_template('index.html')

    return render_template('index.html')


@auth.route('/signup', methods=['POST'])
def signup():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email').strip()
    password = request.form.get('password')
    today_date = date.today().strftime("%Y-%m-%d")

    existing_user = FCD_collection.find_one({'email': email})

    if existing_user:
        return render_template('index.html', error="User already exists")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    FCD_collection.insert_one({
        'FirstName': first_name,
        'LastName': last_name,
        'email': email,
        'password': hashed_password,
        'auth_type': 'local',
        'created_at':today_date
    })

    session['user'] = email
    return redirect(url_for("dashboard.home"))
