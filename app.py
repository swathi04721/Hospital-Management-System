from flask import Flask, render_template
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route('/')
def home():
    return """
    <h1>Hospital Management System</h1>
    <h2>Website deployed successfully 🎉</h2>
    """
    
if __name__ == "__main__":
    app.run(debug=True)