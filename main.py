import os
import sentry_sdk
from flask import Flask, render_template, request, url_for, flash,redirect
from mysql.connector import connect, Error
from dotenv import load_dotenv

sentry_sdk.init("https://7bf8eea90c3d4f71b4ae65ae3de19130@o4505523323076608.ingest.sentry.io/4505523325763584")

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}

@app.route('/')
def Index():
    try:
        with connect(**config) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM students")
            data = cur.fetchall()
            cur.close()

            return render_template('index.html', students=data, maquina=os.uname().nodename)
    except Error as e:
        flash("Error connecting to database: {}".format(e))
        sentry_sdk.capture_exception(e)
        return redirect(url_for('error'))

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        try:
            with connect(**config) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
                conn.commit()
                flash("Data Inserted Successfully")
                cur.close()
                return redirect(url_for('Index'))
        except Error as e:
            flash("Error inserting data: {}".format(e))
            sentry_sdk.capture_exception(e)
            return redirect(url_for('error'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    try:
        with connect(**config) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
            conn.commit()
            flash("Record Has Been Deleted Successfully")
            cur.close()
            return redirect(url_for('Index'))
    except Error as e:
        flash("Error deleting data: {}".format(e))
        sentry_sdk.capture_exception(e)
        return redirect(url_for('error'))

@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        try:
            with connect(**config) as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE students SET name=%s, email=%s, phone=%s
                    WHERE id=%s
                """, (name, email, phone, id_data))
                conn.commit()
                flash("Data Updated Successfully")
                cur.close()
                return redirect(url_for('Index'))
        except Error as e:
            flash("Error updating data: {}".format(e))
            sentry_sdk.capture_exception(e)
            return redirect(url_for('error'))

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
