from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create Table Automatically
cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INTEGER,
    disease VARCHAR(100)
)
""")

conn.commit()


# Login Page
@app.route('/')
def login():
    return render_template('login.html')


# Login Check
@app.route('/login_check', methods=['POST'])
def login_check():

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin123":

        return redirect('/dashboard')

    else:

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )


# Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


# Patient Form
@app.route('/patients')
def patients():
    return render_template('patients.html')


# Add Patient
@app.route('/add_patient', methods=['POST'])
def add_patient():

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']

    query = """
    INSERT INTO patients(name, age, disease)
    VALUES (%s, %s, %s)
    """

    values = (name, age, disease)

    cur.execute(query, values)

    conn.commit()

    return redirect('/view_patients')


# View Patients
@app.route('/view_patients')
def view_patients():

    cur.execute("SELECT * FROM patients")

    patients = cur.fetchall()

    return render_template(
        'view_patients.html',
        patients=patients
    )


if __name__ == "__main__":
    app.run(debug=True)