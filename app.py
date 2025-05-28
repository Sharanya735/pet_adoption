from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import date

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  
        database='pet_adoption_db'
    )
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/view_pets')
def view_pets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Pets WHERE Status = 'Available'")
    pets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_pets.html', pets=pets)

@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
def adopt(pet_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Adopters (FullName, Email, Phone, Address) VALUES (%s, %s, %s, %s)",
                       (name, email, phone, address))
        adopter_id = cursor.lastrowid
        cursor.execute("""
        INSERT INTO Adoptions (PetID, AdopterID, AdoptionDate, Status)
        VALUES (%s, %s, %s, %s)
        """, (pet_id, adopter_id, date.today(), 'Pending'))
        cursor.execute("INSERT INTO Adoptions (PetID, AdopterID, AdoptionDate) VALUES (%s, %s, %s)",
                       (pet_id, adopter_id, date.today()))
        cursor.execute("UPDATE Pets SET Status = 'Adopted' WHERE PetID = %s", (pet_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_pets'))
    return render_template('adopt_form.html', pet_id=pet_id)

@app.route('/admin_dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Pets")
    pets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', pets=pets)

@app.route('/adoption_requests')
def adoption_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT A.AdoptionID, P.Name AS PetName, U.FullName AS AdopterName, A.AdoptionDate, A.Status
        FROM Adoptions A
        JOIN Pets P ON A.PetID = P.PetID
        JOIN Adopters U ON A.AdopterID = U.AdopterID
    """)
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('adoption_requests.html', requests=requests)
@app.route('/update_adoption_status/<int:adoption_id>/<status>')
def update_adoption_status(adoption_id, status):
    if status not in ['Approved', 'Rejected']:
        return "Invalid status", 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Adoptions SET Status = %s WHERE AdoptionID = %s", (status, adoption_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('adoption_requests'))



@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['species'],
            request.form['breed'],
            int(request.form['age']),
            request.form['gender'],
            int(request.form['shelter_id']),
            request.form['status']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Pets (Name, Species, Breed, Age, Gender, ShelterID, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_pet.html')

@app.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['species'],
            request.form['breed'],
            int(request.form['age']),
            request.form['gender'],
            int(request.form['shelter_id']),
            request.form['status'],
            pet_id
        )
        cursor.execute("UPDATE Pets SET Name=%s, Species=%s, Breed=%s, Age=%s, Gender=%s, ShelterID=%s, Status=%s WHERE PetID=%s", data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    cursor.execute("SELECT * FROM Pets WHERE PetID = %s", (pet_id,))
    pet = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_pet.html', pet=pet)

@app.route('/delete_pet/<int:pet_id>')
def delete_pet(pet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pets WHERE PetID = %s", (pet_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="pet_adoption_db"
)
