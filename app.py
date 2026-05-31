from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# -----------------------------
# DATABASE TABLES
# -----------------------------

# Patients Table
cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INTEGER,
    disease VARCHAR(100)
)
""")

# Appointments Table
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    appointment_date VARCHAR(100)
)
""")

# Add status column if missing
try:
    cur.execute("""
    ALTER TABLE appointments
    ADD COLUMN status VARCHAR(50) DEFAULT 'Pending'
    """)
except:
    conn.rollback()

# Doctors Table
cur.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    phone VARCHAR(20)
)
""")

conn.commit()

# -----------------------------
# LOGIN
# -----------------------------

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login_check', methods=['POST'])
def login_check():

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin123":
        return redirect('/dashboard')

    return render_template(
        'login.html',
        error="Invalid Username or Password"
    )

# -----------------------------
# DASHBOARD
# -----------------------------

@app.route('/dashboard')
def dashboard():

    cur.execute("SELECT COUNT(*) FROM patients")
    total_patients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE status='Completed'
    """)
    completed_appointments = cur.fetchone()[0]

    return render_template(
        'index.html',
        total_patients=total_patients,
        total_appointments=total_appointments,
        completed_appointments=completed_appointments
    )

# -----------------------------
# PATIENTS
# -----------------------------

@app.route('/patients')
def patients():
    return render_template('patients.html')


@app.route('/add_patient', methods=['POST'])
def add_patient():

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']

    cur.execute(
        """
        INSERT INTO patients(name, age, disease)
        VALUES (%s, %s, %s)
        """,
        (name, age, disease)
    )

    conn.commit()

    return redirect('/view_patients')


@app.route('/view_patients')
def view_patients():

    cur.execute("SELECT * FROM patients")

    patients = cur.fetchall()

    return render_template(
        'view_patients.html',
        patients=patients
    )


@app.route('/delete/<int:id>')
def delete(id):

    cur.execute(
        "DELETE FROM patients WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_patients')

# -----------------------------
# APPOINTMENTS
# -----------------------------

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')


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

# -----------------------------
# DOCTORS
# -----------------------------

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')


@app.route('/add_doctor', methods=['POST'])
def add_doctor():

    name = request.form['name']
    specialization = request.form['specialization']
    phone = request.form['phone']

    cur.execute("""
    INSERT INTO doctors(name, specialization, phone)
    VALUES (%s, %s, %s)
    """, (name, specialization, phone))

    conn.commit()

    return redirect('/view_doctors')


@app.route('/view_doctors')
def view_doctors():

    cur.execute("SELECT * FROM doctors")

    doctors = cur.fetchall()

    return render_template(
        'view_doctors.html',
        doctors=doctors
    )

# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)