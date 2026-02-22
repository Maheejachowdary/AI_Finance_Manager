from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import mysql
from models.ml_model import predict_next_month
import numpy as np
import os

# Matplotlib setup for Flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/add-income', methods=['GET','POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO income (user_id, amount, date) VALUES (%s, %s, %s)",
            (session['user_id'], request.form['amount'], request.form['date'])
        )
        mysql.connection.commit()
        cur.close()
        flash("Income added successfully!")
        return redirect(url_for('finance.add_income'))

    return render_template('add_income.html')


@finance_bp.route('/add-expense', methods=['GET','POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO expenses (user_id, category, amount, date) VALUES (%s,%s,%s,%s)",
            (session['user_id'], request.form['category'], request.form['amount'], request.form['date'])
        )
        mysql.connection.commit()
        cur.close()
        flash("Expense added successfully!")
        return redirect(url_for('finance.add_expense'))

    return render_template('add_expense.html')


@finance_bp.route('/predict')
def predict_expense():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            EXTRACT(YEAR_MONTH FROM date) AS ym,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id=%s
        GROUP BY ym
        ORDER BY ym
    """, (session['user_id'],))

    results = cur.fetchall()
    cur.close()

    expense_totals = [float(r[1]) for r in results]

    if len(expense_totals) < 2:
        return render_template('prediction.html', prediction=None)

    # Prepare X and y
    X = np.arange(1, len(expense_totals) + 1).reshape(-1, 1)
    y = np.array(expense_totals)

    # Get model outputs
    prediction, mae, r2, model = predict_next_month(expense_totals, return_model=True)

    # Generate predictions for visualization
    predictions = model.predict(X)

    # ===== CREATE ACTUAL VS PREDICTED GRAPH =====
    plt.figure()
    plt.plot(X, y, label="Actual")
    plt.plot(X, predictions, label="Predicted")
    plt.legend()
    plt.title("Actual vs Predicted Expenses")
    plt.xlabel("Month")
    plt.ylabel("Expenses")

    # Ensure static folder exists
    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig("static/model_analysis.png")
    plt.close()

    return render_template(
        'prediction.html',
        prediction=round(prediction, 2),
        mae=round(mae, 2),
        r2=round(r2, 4)
    )