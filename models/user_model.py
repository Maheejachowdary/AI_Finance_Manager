from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mysql

def create_user(name, email, password, mobile):
    password_hash = generate_password_hash(password)

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, mobile) VALUES (%s, %s, %s, %s)",
            (name, email, password_hash, mobile)
        )
        mysql.connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def verify_user(email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user and check_password_hash(user[3], password):
        return user

    return None