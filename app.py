from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin":
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Username or Password"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/patients')
def patients():
    return render_template('patients.html')
@app.route('/add_patient', methods=['POST'])
def add_patient():

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']

    cur.execute(
        "INSERT INTO patients (name, age, disease) VALUES (%s, %s, %s)",
        (name, age, disease)
    )

    conn.commit()

    return redirect('/patients')

if __name__ == '__main__':
    app.run(debug=True)