from flask import Blueprint, render_template, request, jsonify
from db_config import get_db_connection
from datetime import datetime, timedelta

booking_bp = Blueprint('booking', __name__)

# Route: Serve the dashboard page
@booking_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route: Return doctors in JSON format for AJAX calls
@booking_bp.route('/get_doctors/<specialty_name>')
def get_doctors(specialty_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT d.id AS id, d.name AS name
        FROM doctors d
        JOIN specialties s ON d.specialty_id = s.id
        WHERE s.name = %s
    """
    cursor.execute(query, (specialty_name,))
    doctors = cursor.fetchall()
    conn.close()

    return jsonify(doctors)

# Route: GET shows form, POST confirms booking
@booking_bp.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
def book_form(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch doctor's name
    cursor.execute("SELECT id, name FROM doctors WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()

    if not doctor:
        conn.close()
        return "Doctor not found", 404

    if request.method == 'POST':
        selected_time = request.form['appointment_time']
        # Placeholder logic: Insert into a 'bookings' table (assumed schema)
        cursor.execute("""
            INSERT INTO appointments (doctor_id, appointment_time)
            VALUES (%s, %s)
        """, (doctor_id, selected_time))
        conn.commit()
        conn.close()
        return f"<h3 style='color:green;'>Appointment confirmed for {doctor['name']} at {selected_time}</h3>"

    # GET: Generate available time slots
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    end = now + timedelta(days=14)
    delta = timedelta(minutes=30)
    slots = []

    while now <= end:
        if 9 <= now.hour < 17 and now.weekday() < 5:
            slots.append(now)
        now += delta

    conn.close()
    return render_template('book_appointment.html', doctor=doctor, slots=slots)
