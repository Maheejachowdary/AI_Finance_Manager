from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(mysql, name, email, password):
    cur = mysql.connection.cursor()
    hashed = generate_password_hash(password)
    cur.execute("INSERT INTO users (name,email,password_hash) VALUES (%s,%s,%s)", (name,email,hashed))
    mysql.connection.commit()
    cur.close()

def verify_user(mysql, email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
    data = cur.fetchone()
    cur.close()
    if data and check_password_hash(data[0], password):
        return True
    return False
