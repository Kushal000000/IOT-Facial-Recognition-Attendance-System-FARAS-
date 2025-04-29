from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import numpy as np
import urllib.request
from threading import Thread
from flask import send_from_directory
import pymysql
    

app = Flask(__name__, static_folder='students')  # Important for serving images

CORS(app)

ESP32_CAM_URL = "http://192.168.1.73/capture"

class ImageCapture:
    def __init__(self, name, student_id, section, gender):
        self.folder_name = f"{name}_{student_id}_{section}_{gender}"
        self.folder_path = os.path.join("students", self.folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.img_count = 1
        self.running = True

    def capture_images(self):
        print("[INFO] Capturing images...")
        while self.running and self.img_count <= 10:
            try:
                img_resp = urllib.request.urlopen(ESP32_CAM_URL)
                img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                frame = cv2.imdecode(img_np, -1)

                img_filename = os.path.join(self.folder_path, f"img{self.img_count}.jpg")
                cv2.imwrite(img_filename, frame)
                print(f"[SAVED] {img_filename}")
                self.img_count += 1

            except Exception as e:
                print(f"[ERROR] {e}")
                break
        print("[INFO] Done.")

@app.route('/start_enroll', methods=['POST'])
def start_enroll():
    data = request.get_json()
    name = data.get("name", "").replace(" ", "")
    student_id = data.get("student_id", "")
    section = data.get("section", "")
    gender = data.get("gender", "M").upper()

    if not all([name, student_id, section, gender]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    capture = ImageCapture(name, student_id, section, gender)
    thread = Thread(target=capture.capture_images)
    thread.start()

    return jsonify({"status": "success", "message": "Enrollment started"})

@app.route('/capture', methods=['POST'])
def capture_single():
    try:
        folder_name = request.json.get("folder_name")
        if not folder_name:
            return jsonify({"status": "error", "message": "Missing folder_name"}), 400

        folder_path = os.path.join("students", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        img_resp = urllib.request.urlopen(ESP32_CAM_URL)
        img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_np, -1)

        img_count = len(os.listdir(folder_path)) + 1
        img_filename = os.path.join(folder_path, f"img{img_count}.jpg")
        cv2.imwrite(img_filename, frame)

        return jsonify({"status": "success", "message": f"Captured image {img_count}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_student_profile', methods=['POST'])
def get_student_profile():
    try:
        data = request.get_json()
        name = data.get("name", "").replace(" ", "")
        student_id = data.get("student_id", "")
        section = data.get("section", "")
        folder_prefix = f"{name}_{student_id}_{section}"

        db = pymysql.connect(
            host="localhost",
            user="attendance_user",
            password="Kushal_01",
            database="attendance_system"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # Fetch profile from students table
        cursor.execute("""
            SELECT name, student_id, section, gender, phone, email, father_name, mother_name, enrollment_date
            FROM students
            WHERE name=%s AND student_id=%s AND section=%s
        """, (name, student_id, section))
        student_info = cursor.fetchone()

        if not student_info:
            return jsonify({"status": "error", "message": "Student not found"}), 404

        # Fetch logs from attendance_logs table
        cursor.execute("""
            SELECT time_of_entry
            FROM attendance_logs
            WHERE name=%s AND student_id=%s AND section=%s
            ORDER BY time_of_entry ASC
        """, (student_info['name'], student_info['student_id'], student_info['section']))
        attendance_logs = cursor.fetchall()

        # Prepare attendance logs list
        logs = [log['time_of_entry'].strftime("%Y-%m-%d %H:%M:%S") for log in attendance_logs]

        # Calculate present/absent
        present_count = len(logs)
        total_days = 30  # Assumption (you can customize later)
        absent_count = total_days - present_count if total_days >= present_count else 0

        # Prepare image fetching (same logic as before)
        image_url = ""
        students_folder = "students"
        for folder in os.listdir(students_folder):
            if folder.startswith(folder_prefix):
                for file in os.listdir(os.path.join(students_folder, folder)):
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        image_url = f"http://192.168.1.85:5000/static/{folder}/{file}"
                        break
                break
        if not image_url:
            image_url = "https://via.placeholder.com/150"

        return jsonify({
            "status": "success",
            "data": {
                **student_info,
                "image_url": image_url,
                "logs": logs,
                "present_count": present_count,
                "absent_count": absent_count
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/static/<path:filename>')
def serve_student_image(filename):
    return send_from_directory('students', filename)



import re

@app.route('/update_student', methods=['POST'])
def update_student():
    try:
        data = request.get_json()
        
        name = data.get("name", "").strip()
        student_id = data.get("student_id", "").strip()
        section = data.get("section", "").strip()

        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        father = data.get("father_name", "").strip()
        mother = data.get("mother_name", "").strip()
        enrollment_date = data.get("enrollment_date", "").strip()

        db = pymysql.connect(
            host="localhost",
            user="attendance_user",
            password="Kushal_01",
            database="attendance_system"
        )
        cursor = db.cursor()

        # Check if student exists
        cursor.execute("""
            SELECT COUNT(*) FROM students
            WHERE name=%s AND student_id=%s AND section=%s
        """, (name, student_id, section))
        exists = cursor.fetchone()[0]

        if exists == 0:
            return jsonify({"status": "error", "message": "Student not found. Update failed."}), 404

        # ? VALIDATION Starts Here:
        if phone and not phone.isdigit():
            return jsonify({"status": "error", "message": "Phone number must contain only digits."}), 400

        if father and not re.match("^[A-Za-z\s]+$", father):
            return jsonify({"status": "error", "message": "Father's Name must contain only alphabets."}), 400

        if mother and not re.match("^[A-Za-z\s]+$", mother):
            return jsonify({"status": "error", "message": "Mother's Name must contain only alphabets."}), 400

        # ? If everything is valid, proceed to update
        cursor.execute("""
            UPDATE students SET 
                phone=%s, email=%s, father_name=%s, mother_name=%s, enrollment_date=%s
            WHERE name=%s AND student_id=%s AND section=%s
        """, (phone, email, father, mother, enrollment_date, name, student_id, section))

        db.commit()
        return jsonify({"status": "success", "message": "Student info updated successfully."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

