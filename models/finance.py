def add_income(mysql, user_id, amount, source, date):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO income (user_id, amount, source, date) VALUES (%s,%s,%s,%s)",
        (user_id, amount, source, date)
    )
    mysql.connection.commit()
    cur.close()


def add_expense(mysql, user_id, category, amount, date):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO expenses (user_id, category, amount, date) VALUES (%s,%s,%s,%s)",
        (user_id, category, amount, date)
    )
    mysql.connection.commit()
    cur.close()
