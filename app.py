from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create Table Automatically
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    appointment_date VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Pending'
)
""")

conn.commit()
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    appointment_date VARCHAR(100)
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

    cur.execute("SELECT COUNT(*) FROM patients")
    total_patients = cur.fetchone()[0]

    return render_template(
        'index.html',
        total_patients=total_patients
    )

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
# Delete Patient
@app.route('/delete/<int:id>')
def delete(id):

    cur.execute(
        "DELETE FROM patients WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_patients')
# Appointment Form
@app.route('/appointments')
def appointments():
    return render_template('appointments.html')


# Save Appointment
@app.route('/book_appointment', methods=['POST'])
def book_appointment():

    patient_name = request.form['patient_name']
    doctor_name = request.form['doctor_name']
    appointment_date = request.form['appointment_date']

    cur.execute("""
    INSERT INTO appointments
    (patient_name, doctor_name, appointment_date, status)
    VALUES (%s, %s, %s, %s)
""", (
    patient_name,
    doctor_name,
    appointment_date,
    "Pending"
))   
    conn.commit()

    return redirect('/view_appointments')


# View Appointments
@app.route('/view_appointments')
def view_appointments():

    cur.execute("SELECT * FROM appointments")

    appointments = cur.fetchall()

    return render_template(
        'view_appointments.html',
        appointments=appointments
    )
@app.route('/complete_appointment/<int:id>')
def complete_appointment(id):

    cur.execute(
        "UPDATE appointments SET status='Completed' WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_appointments')
if __name__ == "__main__":
    app.run(debug=True)