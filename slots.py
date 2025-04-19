from datetime import datetime, timedelta, time
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Horlicks1",
    database="healthcare_db"
)
cursor = conn.cursor()

start_hour = 9
end_hour = 17
slot_duration_minutes = 30
number_of_days = 14

# Only Monday to Friday
def is_weekday(date):
    return date.weekday() < 5  # 0=Mon, ..., 4=Fri

# Get all doctor IDs dynamically
cursor.execute("SELECT id FROM doctors")
doctor_ids = [row[0] for row in cursor.fetchall()]

# Loop through each doctor and generate slots
for doctor_id in doctor_ids:
    for day_offset in range(number_of_days):
        date = datetime.today().date() + timedelta(days=day_offset)
        
        if not is_weekday(date):
            continue

        current_time = datetime.combine(date, time(hour=start_hour))
        end_time = datetime.combine(date, time(hour=end_hour))

        while current_time < end_time:
            # Check if this slot already exists
            cursor.execute("""
                SELECT COUNT(*) FROM time_slots
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
            """, (doctor_id, date, current_time.time()))
            exists = cursor.fetchone()[0]

            if not exists:
                cursor.execute("""
                    INSERT INTO time_slots (doctor_id, appointment_date, appointment_time)
                    VALUES (%s, %s, %s)
                """, (doctor_id, date, current_time.time()))

            current_time += timedelta(minutes=slot_duration_minutes)

# Commit & close
conn.commit()
cursor.close()
conn.close()

print("Time slots inserted.")