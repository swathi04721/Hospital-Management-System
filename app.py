from flask import Flask, render_template, request, redirect
import os
import psycopg2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file

app = Flask(__name__)
print("APP STARTED")
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
# Medical History Table
cur.execute("""
CREATE TABLE IF NOT EXISTS medical_history (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100),
    disease_history TEXT,
    allergies TEXT,
    treatment_notes TEXT
)
""")

conn.commit()
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

    cur.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE status='Completed'
    """)
    completed_appointments = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount),0) FROM bills")
    total_revenue = cur.fetchone()[0]

    return render_template(
        'index.html',
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        completed_appointments=completed_appointments,
        total_revenue=total_revenue
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
        '''
        INSERT INTO patients(name, age, disease)
        VALUES (%s, %s, %s)
        ''',
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
# Medical History Form
@app.route('/medical_history')
def medical_history():
    return render_template('medical_history.html')


# Save Medical History
@app.route('/add_medical_history', methods=['POST'])
def add_medical_history():

    patient_name = request.form['patient_name']
    disease_history = request.form['disease_history']
    allergies = request.form['allergies']
    treatment_notes = request.form['treatment_notes']

    cur.execute("""
    INSERT INTO medical_history(
        patient_name,
        disease_history,
        allergies,
        treatment_notes
    )
    VALUES (%s,%s,%s,%s)
    """, (
        patient_name,
        disease_history,
        allergies,
        treatment_notes
    ))

    conn.commit()

    return redirect('/view_medical_history')


# View Medical History
@app.route('/view_medical_history')
def view_medical_history():

    cur.execute("SELECT * FROM medical_history")

    records = cur.fetchall()

    return render_template(
        'view_medical_history.html',
        records=records
    )
# Billing Table
cur.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100),
    treatment VARCHAR(100),
    amount DECIMAL(10,2)
)
""")

conn.commit()
# Billing Form
@app.route('/billing')
def billing():
    return render_template('billing.html')


# Save Bill
@app.route('/add_bill', methods=['POST'])
def add_bill():

    patient_name = request.form['patient_name']
    treatment = request.form['treatment']
    amount = request.form['amount']

    cur.execute("""
    INSERT INTO bills(
        patient_name,
        treatment,
        amount
    )
    VALUES (%s,%s,%s)
    """, (
        patient_name,
        treatment,
        amount
    ))

    conn.commit()

    return redirect('/view_bills')


# View Bills
@app.route('/view_bills')
def view_bills():

    cur.execute("SELECT * FROM bills")

    bills = cur.fetchall()

    return render_template(
        'view_bills.html',
        bills=bills
    )
@app.route('/search_patient', methods=['GET', 'POST'])
def search_patient():

    patients = []

    if request.method == 'POST':

        keyword = request.form['keyword']

        cur.execute(
            """
            SELECT * FROM patients
            WHERE name ILIKE %s
            """,
            ('%' + keyword + '%',)
        )

        patients = cur.fetchall()

    return render_template(
        'search_patient.html',
        patients=patients
    )
@app.route('/patient_profile/<int:id>')
def patient_profile(id):

    cur.execute(
        "SELECT * FROM patients WHERE id=%s",
        (id,)
    )
    patient = cur.fetchone()

    cur.execute(
        """
        SELECT *
        FROM appointments
        WHERE patient_name=%s
        """,
        (patient[1],)
    )
    appointments = cur.fetchall()

    return render_template(
        'patient_profile.html',
        patient=patient,
        appointments=appointments
    )
@app.route('/download_bill/<int:id>')
def download_bill(id):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from flask import send_file
    from datetime import datetime

    cur.execute(
        "SELECT * FROM bills WHERE id=%s",
        (id,)
    )

    bill = cur.fetchone()

    pdf_file = f"bill_{id}.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("SMART HOSPITAL", styles['Title'])
    )

    elements.append(
        Paragraph("Hospital Management System", styles['Heading2'])
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"<b>Invoice Number:</b> {bill[0]}", styles['Normal'])
    )

    elements.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y')}",
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"<b>Patient Name:</b> {bill[1]}", styles['Normal'])
    )

    elements.append(
        Paragraph(f"<b>Treatment:</b> {bill[2]}", styles['Normal'])
    )

    elements.append(
        Paragraph(f"<b>Amount:</b> ₹{bill[3]}", styles['Normal'])
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "Thank you for choosing Smart Hospital.",
            styles['Heading3']
        )
    )

    elements.append(
        Paragraph(
            "We wish you a speedy recovery.",
            styles['Normal']
        )
    )

    doc.build(elements)

    return send_file(
        pdf_file,
        as_attachment=True
    )
# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)