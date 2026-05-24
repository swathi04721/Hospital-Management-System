from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mekalaswathi12",
    database="hospital_db"
)

cursor = db.cursor()

# Login Page
@app.route('/')
def login():
    return render_template('login.html')
@app.route('/login_check', methods=['POST'])
def login_check():

    username = request.form['username']
    password = request.form['password']
@app.route('/home')
def home():
    return render_template('home.html')
    # Simple Authentication

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


# Patient Form Page
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

    db.commit()

    return redirect('/view_patients')


# View Patients
@app.route('/view_patients')
def view_patients():

    cursor.execute("SELECT * FROM patients")

    patients = cursor.fetchall()

    return render_template('view_patients.html', patients=patients)


# Delete Patient
@app.route('/delete_patient/<int:id>')
def delete_patient(id):

    query = "DELETE FROM patients WHERE patient_id = %s"

    cursor.execute(query, (id,))

    db.commit()

    return redirect('/view_patients')


# Edit Patient Page
@app.route('/edit_patient/<int:id>')
def edit_patient(id):

    query = "SELECT * FROM patients WHERE patient_id = %s"

    cursor.execute(query, (id,))

    patient = cursor.fetchone()

    return render_template('edit_patient.html', patient=patient)


# Update Patient
@app.route('/update_patient/<int:id>', methods=['POST'])
def update_patient(id):

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']
    phone = request.form['phone']

    query = """
    UPDATE patients
    SET name=%s, age=%s, disease=%s, phone=%s
    WHERE patient_id=%s
    """

    values = (name, age, disease, phone, id)

    cursor.execute(query, values)

    db.commit()

    return redirect('/view_patients')
# AI Predictor Page
@app.route('/ai_predictor')
def ai_predictor():
    return render_template('ai_predictor.html')


# AI Prediction Logic
@app.route('/predict', methods=['POST'])
def predict():

    age = int(request.form['age'])
    heart_rate = int(request.form['heart_rate'])
    sugar = int(request.form['sugar'])

    # Simple AI Logic

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

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)