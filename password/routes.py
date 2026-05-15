from flask import Blueprint , render_template , redirect , url_for , request , session
from utils.db import FCD_collection
from utils.mail import send_otp_email
import bcrypt
from flask import jsonify
import secrets
import time

password = Blueprint('password',__name__)

@password.route('/forgot-password')
def forgot_password():
    return render_template('forgot.html')

@password.route('/check-forgot-email' , methods=["POST"])
def check_email():
    data = request.get_json()
    email = data.get('email')

    user = FCD_collection.find_one({'email': email})

    return jsonify({
        "exists": True if user else False,
        "auth_type": user.get("auth_type") if user else None
    })

@password.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')

    user = FCD_collection.find_one({'email': email})

    if not user:
        return render_template('forgot.html', error="Invalid Email Id")

    if user.get("auth_type") != "local":
        return render_template(
            'forgot.html',
            error=f"This account was created using {user.get('auth_type')} login."
        )

    otp = str(secrets.randbelow(900000) + 100000)

    session['otp'] = otp
    session['reset_email'] = email
    session['otp_time'] = time.time()

    if send_otp_email(email, otp):
        return redirect(url_for('password.otp_page'))
    else:
        return render_template('forgot.html', error="Network error. Try again.")

@password.route('/otp')
def otp_page():
    return render_template('otp.html')

@password.route('/verify-otp', methods=['POST'])
def verify_otp():
    user_otp = (
        request.form.get('otp1') +
        request.form.get('otp2') +
        request.form.get('otp3') +
        request.form.get('otp4') +
        request.form.get('otp5') +
        request.form.get('otp6')
    )

    if 'otp' not in session:
        return render_template('otp.html', error="Session expired")

    if time.time() - session.get('otp_time', 0) > 180:
        return render_template('otp.html', error="OTP expired")

    if user_otp == session.get('otp'):
        return redirect(url_for('password.reset_password'))
    else:
        return render_template('otp.html', error="Invalid OTP")

@password.route('/change-password')
def change_password():
    return render_template('Curr_Password.html')

@password.route('/verify-password', methods=['POST'])
def verify_password():

    if 'user' not in session:
        return jsonify({"correct": False})

    email = session['user']

    data = request.get_json()

    if data:
        entered_password = data.get('password')
    else:
        entered_password = request.form.get('password')  # fallback

    user = FCD_collection.find_one({'email': email})

    if not user:
        return jsonify({"correct": False})

    stored_password = user.get('password')

    if bcrypt.checkpw(entered_password.encode('utf-8'), stored_password):
        return jsonify({"correct": True})
    else:
        return jsonify({"correct": False})

@password.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = session.get('reset_email')

        if new_password != confirm_password:
            return render_template('reset.html',error='Password Mismatch')

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        FCD_collection.update_one(
            {'email': email},
            {'$set': {'password': hashed_password}}
        )

        session.pop('otp', None)
        session.pop('reset_email', None)
        return redirect(url_for('auth.index'))
    return render_template('reset.html')

@password.route('/reset-logged-password', methods=['GET', 'POST'])
def reset_logged_password():
    if request.method == 'POST':
        new_password = request.form.get('password')
        new_password = new_password.strip()
        confirm_password = request.form.get('confirm_password')
        confirm_password = confirm_password.strip()
        email = session['user']

        if new_password != confirm_password:
            return render_template('reset-logged.html',error='Password Mismatch')

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        FCD_collection.update_one(
            {'email': email},
            {'$set': {'password': hashed_password}}
        )
        return redirect(url_for('dashboard.profile'))
    return render_template('reset-logged.html')