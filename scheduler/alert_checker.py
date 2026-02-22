from flask_mail import Message
from extensions import mysql
from datetime import datetime


def check_expense_alerts(app):
    """
    Called by APScheduler.
    Checks monthly expenses vs threshold.
    Prevents duplicate alerts within same month.
    """

    print("🔍 Running expense alert check...")

    with app.app_context():
        from app import mail

        cur = mysql.connection.cursor()

        # Get users exceeding threshold this month
        cur.execute("""
            SELECT 
                alerts.user_id,
                alerts.email,
                alerts.threshold,
                alerts.last_alert_sent,
                SUM(expenses.amount) AS total
            FROM alerts
            JOIN expenses 
              ON alerts.user_id = expenses.user_id
            WHERE MONTH(expenses.date) = MONTH(CURDATE())
              AND YEAR(expenses.date) = YEAR(CURDATE())
            GROUP BY alerts.user_id, alerts.email, alerts.threshold, alerts.last_alert_sent
            HAVING total > alerts.threshold
        """)

        results = cur.fetchall()

        if not results:
            print("ℹ️ No alerts triggered this cycle.")
            cur.close()
            return

        today = datetime.today()
        current_month = today.month
        current_year = today.year

        for user_id, email, threshold, last_alert_sent, total in results:

            send_email = False

            # ✅ If never sent before
            if last_alert_sent is None:
                send_email = True
            else:
                # last_alert_sent is DATE type
                if (last_alert_sent.month != current_month or
                        last_alert_sent.year != current_year):
                    send_email = True

            if send_email:

                print(f"⚠️ Alert triggered | User {user_id} | ₹{total} > ₹{threshold}")

                msg = Message(
                    subject="⚠️ Expense Alert: Monthly Limit Exceeded",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f"""Hello,

🚨 Your monthly expense alert has been triggered.

• Alert Limit : ₹{threshold}
• Current Spend : ₹{total}

Please review your expenses.

— AI Finance Manager
"""
                )

                try:
                    mail.send(msg)

                    # ✅ Update alert date to today
                    update_cur = mysql.connection.cursor()
                    update_cur.execute("""
                        UPDATE alerts
                        SET last_alert_sent = CURDATE()
                        WHERE user_id = %s
                    """, (user_id,))
                    mysql.connection.commit()
                    update_cur.close()

                    print(f"📧 Email SENT to {email}")

                except Exception as e:
                    print(f"❌ Email FAILED for {email}")
                    print("Error:", e)

            else:
                print(f"⛔ Alert already sent this month for user {user_id}")

        cur.close()