from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL Connection
DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

cursor = conn.cursor()

# Home Page
@app.route('/home')
def home():
    return render_template('home.html')


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

    try:
        cursor.execute("SELECT COUNT(*) FROM patients")

        total_patients = cursor.fetchone()[0]

    except:
        total_patients = 0

    return render_template(
        'index.html',
        total_patients=total_patients
    )


# Add Patient Page
@app.route('/patients')
def patients():
    return render_template('patients.html')


# Add Patient
@app.route('/add_patient', methods=['POST'])
def add_patient():

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']
    phone = request.form['phone']

    query = """
    INSERT INTO patients(name, age, disease, phone)
    VALUES (%s, %s, %s, %s)
    """

    values = (name, age, disease, phone)

    cursor.execute(query, values)

    conn.commit()

    return redirect('/view_patients')


# View Patients
@app.route('/view_patients')
def view_patients():

    cursor.execute("SELECT * FROM patients")

    patients = cursor.fetchall()

    return render_template(
        'view_patients.html',
        patients=patients
    )


# Delete Patient
@app.route('/delete_patient/<int:id>')
def delete_patient(id):

    cursor.execute(
        "DELETE FROM patients WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect('/view_patients')


# AI Predictor Page
@app.route('/ai_predictor')
def ai_predictor():
    return render_template('ai_predictor.html')


# AI Prediction
@app.route('/predict', methods=['POST'])
def predict():

    age = int(request.form['age'])
    heart_rate = int(request.form['heart_rate'])
    sugar = int(request.form['sugar'])

    if age > 60 or sugar > 180 or heart_rate > 120:

        result = "🔴 High Health Risk"

    elif age > 40 or sugar > 140:

        result = "🟠 Medium Health Risk"

    else:

        result = "🟢 Low Health Risk"

    return render_template(
        'ai_predictor.html',
        result=result
    )


if __name__ == '__main__':
    app.run(debug=True)