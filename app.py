from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app=Flask(__name__)
app.secret_key = "student-management-secret"

def get_connection():
    return mysql.connector.connect(
        host="localhost", 
        user="system",
        password="123456789",
        database="mydatabase",
    )

def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL , 
            email VARCHAR(100) NOT NULL ,
            course VARCHAR(100) NOT NULL
        ) 
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    success = None

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email,hashed_password)
            )
            conn.commit()
            success = "Signup Successfully! Please login."
        except:
            success = "Username already exists!"
        finally:
            conn.close()

    return render_template('signup.html', success=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    err = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']  
            return redirect(url_for('index'))     
        else:
            err = "Invalid Username or Password!"

    return render_template('login.html', err=err)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['GET' , 'POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        course=request.form['course']

        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO students (name , email , course) VALUES (%s , %s , %s) " ,
                       (name ,email ,course))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET' , 'POST'])
def edit_student(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students  WHERE id=%s " , (id,)) 
    students =cursor.fetchone()

    if request.method=='POST':
            name=request.form['name']
            email=request.form['email']
            course=request.form['course']

            cursor.execute("UPDATE students  SET name=%s , email=%s , course=%s   WHERE id=%s " , (name ,email ,course ,id)) 
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
    conn.close()
    return render_template('edit.html' , students=students)

@app.route('/delete/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM students  WHERE id=%s " , (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__=='__main__':
    init_db()
    app.run(debug=True)
         
    

