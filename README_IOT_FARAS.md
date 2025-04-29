# IoT Facial Recognition Attendance System – Final Year Project

This is a complete **IoT-based Facial Recognition Attendance System** developed as a Final Year Project (FYP). The system provides a seamless, contactless attendance mechanism using facial recognition, integrated with ESP32-CAM for video streaming, Raspberry Pi for processing, and real-time GUI access via Django and Flask APIs.

## 🔧 Technologies Used

- **Programming Languages:** Python, HTML, CSS, JavaScript
- **Frameworks:** Flask (for API), Django (for GUI)
- **Database:** MySQL/MariaDB (hosted on Raspberry Pi), SQLite3 (for Django GUI)
- **Hardware:** Raspberry Pi, ESP32-CAM, I2C LCD Display, Breadboard, Wires, Power Supply

## 🎯 Key Features

- Face detection and recognition using OpenCV and face_recognition library
- Live ESP32-CAM video stream for real-time detection
- LCD messages for user feedback (e.g., “Detecting…”, “Attendance Logged”)
- Prevention of duplicate attendance within 12 hours
- Centralized MySQL database logging (name, ID, section, gender, timestamp, etc.)
- Manual entry of profile details after successful face detection
- Django GUI for viewing, filtering, and exporting logs and analytics
- Student profile display with dynamic images and data

## ⚙️ System Architecture

```
[ESP32-CAM]
     ↓ (video stream)
[Raspberry Pi with Flask]
     ↓
[Face Recognition Logic]
     ↓
[MySQL/MariaDB Database]
     ↓
[Django GUI on Laptop/Desktop]
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Django 4.x
- Flask
- MySQL/MariaDB
- ESP32-CAM setup with video stream (e.g., `/video` endpoint)
- I2C LCD display connected to Raspberry Pi

### Clone Repository

```bash
git clone https://github.com/Kushal000000/IOT-Facial-Recognition-Attendance-System-FARAS-.git
cd IOT-Facial-Recognition-Attendance-System-FARAS-
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Setup MySQL Database

- Create a database (e.g., `attendance_db`)
- Create required tables (e.g., `attendance_logs`)
- Update database credentials in the Flask and Django settings

### Running Flask API on Raspberry Pi

```bash
python3 flask_face_enroll.py
```

This handles:
- Face detection and logging
- Image capturing for enrollment
- API for profile and attendance logs

### Running Django GUI

```bash
cd attendance_gui_django
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/` to access the GUI.

## 🗃️ Folder Structure (Partial)

```
IOT-Facial-Recognition-Attendance-System-FARAS-/
│
├── flask_face_enroll.py      # Flask API server
├── face_recognition_feed.py  # Recognition logic
├── lcd_display.py            # I2C LCD control
├── attendance_gui_django/    # Django GUI app
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS
│   ├── views.py              # GUI logic
│   └── urls.py               # URL routing
├── students/                 # Folder for enrolled face images
├── requirements.txt
└── README.md
```

## 📝 Final Year Project Scope

- Designed for educational institutions and corporate environments
- Uses AI-based facial recognition for secure and automated attendance
- User-friendly interface and scalable backend
- Real-time feedback through LCD and GUI
- Includes pre/post survey results, system design, and academic documentation

## 🤝 Contributing

This project is a final year academic submission. Contributions are welcome for learning purposes.

## 📄 License

This repository is for educational use only. Attribution is appreciated.

## 🙋‍♂️ Author

**Kushal [@Kushal000000](https://github.com/Kushal000000)**  
Final Year BSc CS Student  
Contact via GitHub for queries or collaboration.