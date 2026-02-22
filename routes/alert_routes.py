from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import mysql

alert_bp = Blueprint('alert', __name__)

# ---------------- SET ALERT PAGE ----------------
@alert_bp.route('/set-alert', methods=['GET', 'POST'])
def set_alert():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form['email']
        threshold = request.form['threshold']
        user_id = session['user_id']

        cur = mysql.connection.cursor()

        # One alert per user (UPDATE if exists)
        cur.execute("""
            INSERT INTO alerts (user_id, email, threshold)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                email = VALUES(email),
                threshold = VALUES(threshold)
        """, (user_id, email, threshold))

        mysql.connection.commit()
        cur.close()

        flash("Expense alert saved successfully!")
        return redirect(url_for('dashboard'))

    return render_template('set_alert.html')


# ---------------- TEST MAIL ----------------
@alert_bp.route('/test-mail')
def test_mail():
    return "Test route OK"
