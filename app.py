from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# ✅ MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Change if you have a different username
    password="Horlicks!1",  # Your MySQL password
    database="healthcare_db"
)
cursor = db.cursor()

# ✅ Route for login page
@app.route('/')
def login():
    return render_template('login.html')

# ✅ Route to handle login form submission
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=SHA2(%s, 256)", (username, password))
    user = cursor.fetchone()

    if user:
        session['user'] = username  # Store username in session
        flash('Login successful!', 'success')
        return redirect('/dashboard')
    else:
        flash('Login failed! Invalid credentials.', 'danger')
        return redirect('/')

# ✅ Dashboard Route (After Login)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    else:
        flash('You must be logged in to access the dashboard.', 'warning')
        return redirect('/')

# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
