from flask import Flask, render_template, request, redirect
from db import get_connection
from mysql.connector import Error

app = Flask(__name__)

@app.route("/")
def index():
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM accounts")
    accounts = cur.fetchall()
    return render_template("index.html", accounts=accounts)


@app.route("/accounts")
def manage_accounts():
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM accounts")
    accounts = cur.fetchall()
    return render_template("manage_accounts.html", accounts=accounts)


@app.route("/add_account", methods=["POST"])
def add_account():
    name = request.form["name"]
    type = request.form["type"]

    if name.strip() == "" or type.strip() == "":
        db = get_connection()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM accounts")
        accounts = cur.fetchall()
        return render_template("index.html", accounts=accounts, error="Account Name and Type cannot be empty")

    db = get_connection()
    cur = db.cursor()
    cur.execute("INSERT INTO accounts (account_name, type) VALUES (%s,%s)", (name, type))
    db.commit()
    return redirect("/")



@app.route("/update_account", methods=["POST"])
def update_account():
    acc_id = request.form["account_id"]
    name = request.form["name"]
    type = request.form["type"]
    db = get_connection()
    cur = db.cursor()
    cur.execute("UPDATE accounts SET account_name=%s, type=%s WHERE account_id=%s", (name, type, acc_id))
    db.commit()
    return redirect("/accounts")


@app.route("/delete_account/<int:id>", methods=["POST"])
def delete_account(id):
    db = get_connection()
    cur = db.cursor()
    cur.execute("DELETE FROM accounts WHERE account_id=%s", (id,))
    db.commit()
    return redirect("/accounts")


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    acc = request.form["account_id"]
    amount = request.form["amount"]
    desc = request.form["desc"]

    try:
        db = get_connection()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO transactions (account_id, txn_date, amount, description) VALUES (%s, CURDATE(), %s, %s)",
            (acc, amount, desc)
        )
        db.commit()
        return redirect("/report")
    except Error:
        db.rollback()
        db = get_connection()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM accounts")
        accounts = cur.fetchall()
        return render_template("index.html", accounts=accounts, error="Invalid Account ID. Please create the account first.")


@app.route("/report")
def report():
    db = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT a.account_name, SUM(t.amount) AS total
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        GROUP BY a.account_name
    """)
    report = cur.fetchall()
    return render_template("report.html", report=report)

@app.route("/budget")
def budget():
    db = get_connection()
    cur = db.cursor(dictionary=True)

    cur.execute("""
    SELECT 
        a.account_name,
        IFNULL(b.total_budget, 0) AS budget,
        IFNULL(t.total_actual, 0) AS actual
    FROM accounts a

    LEFT JOIN (
        SELECT account_id, SUM(amount) AS total_budget
        FROM budgets
        GROUP BY account_id
    ) b ON a.account_id = b.account_id

    LEFT JOIN (
        SELECT account_id, SUM(amount) AS total_actual
        FROM transactions
        GROUP BY account_id
    ) t ON a.account_id = t.account_id
""")

    budgets = cur.fetchall()
    return render_template("budget.html", budgets=budgets)

@app.route("/add_budget", methods=["POST"])
def add_budget():
    acc = request.form["account_id"]
    year = request.form["year"]
    amt = request.form["amount"]

    db = get_connection()
    cur = db.cursor()
    cur.execute("INSERT INTO budgets (account_id, year, amount) VALUES (%s,%s,%s)", (acc, year, amt))
    db.commit()
    return redirect("/budget")


if __name__ == "__main__":
    app.run(debug=True)
