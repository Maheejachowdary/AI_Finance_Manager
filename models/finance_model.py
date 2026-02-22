from extensions import mysql
from models.alert_model import trigger_alert
from datetime import datetime, timedelta

# ------------------------------
# 1️⃣ Fetch Monthly Expenses
# ------------------------------
def get_monthly_expenses(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT YEAR(date), MONTH(date), SUM(amount)
        FROM expenses
        WHERE user_id=%s
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY YEAR(date), MONTH(date)
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    return [float(row[2]) for row in rows]


# ------------------------------
# 2️⃣ Save Prediction
# ------------------------------
def save_prediction(user_id, month, predicted_amount):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO predictions (user_id, month, predicted_amount)
        VALUES (%s, %s, %s)
    """, (user_id, month, predicted_amount))
    mysql.connection.commit()
    cur.close()


# ------------------------------
# 3️⃣ Check Alerts
# ------------------------------
def check_expenses_alerts(app):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, threshold FROM alerts")
    users = cur.fetchall()

    for user in users:
        user_id, email, threshold = user
        cur.execute("""
            SELECT predicted_amount
            FROM predictions
            WHERE user_id=%s
            ORDER BY month DESC
            LIMIT 1
        """, (user_id,))
        result = cur.fetchone()
        if result:
            predicted_expense = float(result[0])
            if predicted_expense > threshold:
                trigger_alert(app, email, predicted_expense)
    cur.close()


# ------------------------------
# 4️⃣ Helper for ML
# ------------------------------
def get_expense_data_for_ml(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT YEAR(date), MONTH(date), SUM(amount)
        FROM expenses
        WHERE user_id=%s
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY YEAR(date), MONTH(date)
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    X = [i+1 for i in range(len(rows))]
    y = [float(row[2]) for row in rows]
    return X, y


# ------------------------------
# 5️⃣ Next Month Name
# ------------------------------
def next_month():
    today = datetime.today()
    next_month_date = today.replace(day=28) + timedelta(days=4)
    return next_month_date.strftime('%b')
