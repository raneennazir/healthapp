from flask import Flask, render_template, request, redirect, session, url_for, flash
from db_config import get_db_connection
from booking import booking_bp

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' 

app.register_blueprint(booking_bp)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = SHA2(%s, 256)"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user'] = user['username']
        session['user_id'] = user['id']
        return redirect(url_for('booking.dashboard')) 
    else:
        flash("Invalid credentials. Please try again.")
        return redirect(url_for('home'))

# Sign-Up Page
@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

# Sign-Up Logic
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if username is already taken
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash("Username already taken.")
        cursor.close()
        conn.close()
        return redirect(url_for('signup_page'))

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, SHA2(%s, 256))",
        (username, password)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Signup successful!")
    return redirect(url_for('home'))

# Logout logic
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)