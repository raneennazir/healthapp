from datetime import datetime, timedelta, time
import mysql.connector

def insert_slots():
    # Establish database connection
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Horlicks!1',
        database='healthcare_db'
    )
    cursor = conn.cursor()

    # Define time range and interval for slots
    start_time = time(9, 0)
    end_time = time(17, 0)
    interval = timedelta(minutes=30)

    # Get today's date
    today = datetime.today().date()

    # Fetch all doctors
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()

    # Loop through each doctor and insert time slots for the next 14 days
    for doctor in doctors:
        doctor_name = doctor[1]
        print(f"Inserting slots for {doctor_name}")

        for day_offset in range(14):  # For the next 14 days
            date = today + timedelta(days=day_offset)
            current_time = datetime.combine(date, start_time)

            # Loop through each half-hour time slot for the doctor
            while current_time.time() < end_time:
                appointment_time = current_time.time()

                # Insert slot into the appointments table (no doctor_id, using doctor_name)
                cursor.execute("""
                    INSERT INTO appointments (doctor_name, patient_name, appointment_date, appointment_time)
                    VALUES (%s, %s, %s, %s)
                """, (doctor_name, "", date, appointment_time))

                # Move to the next slot (30 minutes later)
                current_time += interval

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()

# Run the function to insert slots
insert_slots()
