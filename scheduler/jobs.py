from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from extensions import mysql
from datetime import datetime


def check_expense_alerts(app):
    """
    Sends ONLY ONE alert email per user per day
    when monthly expense exceeds threshold.
    """
    with app.app_context():
        from app import mail

        cur = mysql.connection.cursor()

        query = """
            SELECT 
                a.user_id,
                a.email,
                a.threshold,
                SUM(e.amount) AS total
            FROM alerts a
            JOIN expenses e ON a.user_id = e.user_id
            WHERE MONTH(e.date) = MONTH(CURDATE())
              AND YEAR(e.date) = YEAR(CURDATE())
              AND (
                    a.last_alert_sent IS NULL
                    OR a.last_alert_sent < CURDATE()
                  )
            GROUP BY a.user_id, a.email, a.threshold, a.last_alert_sent
            HAVING total > a.threshold
        """

        cur.execute(query)
        results = cur.fetchall()

        print("🔍 Alert check executed at", datetime.now())
        print("🔍 Results:", results)

        for user_id, email, threshold, total in results:
            try:
                # 🔒 IMPORTANT: Update FIRST to prevent duplicates
                update_query = """
                    UPDATE alerts
                    SET last_alert_sent = NOW()
                    WHERE user_id = %s
                """
                cur.execute(update_query, (user_id,))
                mysql.connection.commit()

                msg = Message(
                    subject="⚠️ Expense Alert: Limit Exceeded",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f"""
Hello,

Your monthly expense limit is ₹{threshold}.
Your current spending is ₹{total}.

Please review your expenses.

— AI Finance Manager
"""
                )

                mail.send(msg)
                print(f"📧 Email SENT to {email}")

            except Exception as e:
                print(f"❌ Failed to send email to {email}")
                print(e)

        cur.close()


def start_scheduler(app):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=check_expense_alerts,
        trigger="interval",
        minutes=1,   # testing
        args=[app],
        id="expense_alert_job",
        replace_existing=True,
        max_instances=1   # 🔒 prevents overlapping runs
    )

    scheduler.start()
    print("✅ Alert Scheduler STARTED")
