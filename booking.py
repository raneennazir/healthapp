from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from db_config import get_db_connection
from datetime import datetime, timedelta
from datetime import datetime, time

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
@booking_bp.route('/get_slots', methods=['POST'])
def get_slots():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    print(f"Incoming JSON: {data}")
    print(f" Fetching slots for Doctor ID: {doctor_id} on {date}")
    print(f" doctor_id: {doctor_id}, date: {date} (type: {type(date)})")


    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT appointment_time FROM time_slots 
        WHERE doctor_id = %s 
        AND appointment_date = %s 
        AND is_booked = 0
    """
    cursor.execute(query, (doctor_id, date))
    slots = cursor.fetchall()

    print(f" Raw slots: {slots}")

    formatted_slots = []

    for row in slots:
        appt_time = row[0] 
        try:
            if isinstance(appt_time, str):
                display_time = datetime.strptime(appt_time, "%H:%M:%S").strftime("%I:%M %p")
            elif isinstance(appt_time, time):
                display_time = datetime.combine(datetime.today(), appt_time).strftime("%I:%M %p")
            else:
                display_time = str(appt_time)
            formatted_slots.append(display_time)
        except Exception as e:
            print(f"Time formatting error: {e}")
            continue

    conn.close()

    print(f"Formatted Slots: {formatted_slots}")

    return jsonify({'slots': formatted_slots})
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
        patient_name = request.form['patient_name']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']

        try:
          if len(appointment_time.split(':')) == 3:
            time_obj = datetime.strptime(appointment_time, "%H:%M:%S").time()
          else:
            time_obj = datetime.strptime(appointment_time, "%I:%M %p").time()
        except Exception as e:
            print(f"Time parse error: {e}")
            return "Invalid time format", 400
        
        cursor.execute("""
            SELECT * FROM appointment
            WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
        """, (doctor_id, appointment_date, time_obj))
        existing = cursor.fetchone()

        if existing:
            flash("That slot is already booked! Pick another one, my dear scheduler.")
            dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
            conn.close()
            return render_template('book_appointment.html', doctor=doctor, dates=dates)

        # Save appointment
        cursor.execute("""
            INSERT INTO appointment (doctor_id, patient_name, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
        """, (doctor_id, patient_name, appointment_date, time_obj))

        cursor.execute("""
            UPDATE time_slots 
            SET is_booked = 1 
            WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
        """, (doctor_id, appointment_date, time_obj))

        conn.commit()
        conn.close()
        return render_template('appointment_status.html', status="Confirmed", time=appointment_time)

    # GET request: render the booking form
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
    conn.close()
    return render_template('book_appointment.html', doctor=doctor, dates=dates)