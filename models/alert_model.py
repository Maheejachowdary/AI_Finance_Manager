from flask_mail import Message
from extensions import mail

def trigger_alert(app, user_email, predicted_expense):
    """
    Send alert email to user if predicted expense exceeds threshold.
    """
    subject = "🚨 Expense Alert from AI Finance Manager"
    body = f"Hi,\n\nYour predicted next month expense is ₹{predicted_expense}.\nPlease take necessary action!\n\n- AI Finance Manager"

    with app.app_context():
        msg = Message(subject,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[user_email])
        msg.body = body
        mail.send(msg)
