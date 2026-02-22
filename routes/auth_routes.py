from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models .user_model import create_user, verify_user
from extensions import mysql
from utils.otp_utils import generate_otp
from utils.sms_utils import send_otp_sms

auth_bp = Blueprint('auth', __name__)

# ---------------- REGISTER ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']  # NEW FIELD

        if create_user(name, email, password, mobile):
            flash('Registration Successful!')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating user')

    return render_template('register.html')


# ---------------- LOGIN (STEP 1: PASSWORD CHECK) ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = verify_user(email, password)

        if user:
            user_id = user[0]
            mobile = user[4]  # mobile column

            otp = generate_otp()

            # Store OTP in database
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO otp_verification (mobile, otp, created_at) VALUES (%s,%s,NOW())",
                (mobile, otp)
            )
            mysql.connection.commit()

            # Send OTP to mobile
            send_otp_sms(mobile, otp)

            # Store temp user id in session
            session['temp_user_id'] = user_id

            flash('OTP sent to your registered mobile number')
            return redirect(url_for('auth.verify_otp'))

        else:
            flash('Invalid Credentials')

    return render_template('login.html')


# ---------------- VERIFY OTP (STEP 2: FINAL AUTH) ----------------
@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        user_id = session.get('temp_user_id')

        if not user_id:
            return redirect(url_for('auth.login'))

        cur = mysql.connection.cursor()

        # Get user's mobile
        cur.execute("SELECT mobile FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        mobile = user[0]

        # Verify OTP within 5 minutes
        cur.execute("""
            SELECT * FROM otp_verification
            WHERE mobile=%s AND otp=%s
            AND created_at >= NOW() - INTERVAL 5 MINUTE
        """, (mobile, user_otp))

        result = cur.fetchone()

        if result:
            # Delete used OTP
            cur.execute("DELETE FROM otp_verification WHERE mobile=%s", (mobile,))
            mysql.connection.commit()

            # Clear temp session
            session.pop('temp_user_id', None)

            # Final login session
            session['user_id'] = user_id
            session['user'] = mobile

            flash('Login Successful!')
            return redirect(url_for('dashboard'))

        else:
            flash('Invalid or expired OTP')

    return render_template('verify_otp.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))