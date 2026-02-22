import os
from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
from extensions import mysql, mail
from routes.auth_routes import auth_bp
from routes.finance_routes import finance_bp
from routes.alert_routes import alert_bp
from scheduler.jobs import start_scheduler

# ---------------- LOAD ENV VARIABLES ----------------
load_dotenv()

app = Flask(__name__)

# ---------------- SECRET KEY ----------------
app.secret_key = os.getenv("SECRET_KEY")

# ---------------- MYSQL CONFIG ----------------
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

# ---------------- MAIL CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

# ---------------- INIT EXTENSIONS ----------------
mysql.init_app(app)
mail.init_app(app)

# ---------------- REGISTER BLUEPRINTS ----------------
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(finance_bp, url_prefix='/finance')
app.register_blueprint(alert_bp, url_prefix='/alert')

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    session.clear()
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
    """, (session['user_id'],))

    data = cur.fetchall()
    cur.close()

    categories = ['Food', 'Travel', 'Rent', 'Utilities', 'Education']
    expense_values = [0] * 5

    for cat, amt in data:
        if cat in categories:
            expense_values[categories.index(cat)] = float(amt)

    return render_template('dashboard.html', expense_values=expense_values)

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    start_scheduler(app)
    app.run(debug=False, use_reloader=False)
