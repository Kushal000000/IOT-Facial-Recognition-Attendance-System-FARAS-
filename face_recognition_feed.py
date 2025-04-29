import cv2
import face_recognition
import urllib.request
import numpy as np
import pymysql
import time
from datetime import datetime, timedelta
from load_known_faces import get_known_faces
from RPLCD.i2c import CharLCD

# === CONFIGURATIONS ===
ESP32_STREAM_URL = "http://192.168.1.73/capture"

# Load known face encodings
known_face_encodings, known_face_names = get_known_faces()

# LCD initialization
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)

# === HELPER FUNCTIONS ===

def show_lcd_message(message, delay=2):
    lcd.clear()
    lcd.write_string(message[:32])  # Limit message to LCD size
    time.sleep(delay)
    lcd.clear()

def connect_to_database():
    try:
        return pymysql.connect(
            host='localhost',
            user='attendance_user',
            password='Kushal_01',
            database='attendance_system'
        )
    except pymysql.Error as e:
        print(f"? DB connection error: {e}")
        return None

def has_logged_in_last_12_hours(student_id):
    connection = connect_to_database()
    if not connection:
        return False
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT time_of_entry FROM attendance_logs
                WHERE student_id = %s
                ORDER BY time_of_entry DESC LIMIT 1
            """
            cursor.execute(sql, (student_id,))
            result = cursor.fetchone()
            if result:
                last_time = result[0]
                if datetime.now() - last_time < timedelta(hours=12):
                    return True
        return False
    except pymysql.Error as e:
        print(f"? DB check error: {e}")
        return False
    finally:
        connection.close()

def insert_attendance(name, student_id, section, gender):
    connection = connect_to_database()
    if not connection:
        return
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO attendance_logs (name, student_id, section, gender)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, student_id, section, gender))
            connection.commit()
            print(f"? Attendance logged for {name}")
            show_lcd_message(f"Logged: {name}", delay=3)
            show_lcd_message("Please wait...", delay=5)
    except pymysql.Error as e:
        print(f"? DB insert error: {e}")
    finally:
        connection.close()

def extract_student_details(folder_name):
    try:
        name, student_id, section, gender = folder_name.split('_')
        return name, student_id, section, gender
    except ValueError:
        print("? Invalid folder name format")
        return None, None, None, None

def get_frame():
    try:
        img_resp = urllib.request.urlopen(ESP32_STREAM_URL)
        img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_np, -1)
        return frame
    except Exception as e:
        print(f"? Frame error: {e}")
        return None

# === MAIN LOOP ===

show_lcd_message("Please face the camera", delay=3)

while True:
    frame = get_frame()
    if frame is None:
        continue

    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Speed boost
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    if face_locations:
        show_lcd_message("Detecting face...", delay=1)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_face_names[match_index]
            name, student_id, section, gender = extract_student_details(name)

            if all([name, student_id, section, gender]):
                if not has_logged_in_last_12_hours(student_id):
                    insert_attendance(name, student_id, section, gender)
                else:
                    print(f"? {name} already logged within last 12 hours")
                    show_lcd_message("Already Logged", delay=3)
                    show_lcd_message("Please wait...", delay=5)

        # Draw boxes (rescale coords since we resized image)
        scale = 2
        top, right, bottom, left = top*scale, right*scale, bottom*scale, left*scale
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("ESP32-CAM Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
