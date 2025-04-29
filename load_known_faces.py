import face_recognition
import os

STUDENTS_DIR = "students"

def get_known_faces():
    known_face_encodings = []
    known_face_names = []

    # Iterate over student folders
    for student_name in os.listdir(STUDENTS_DIR):
        student_path = os.path.join(STUDENTS_DIR, student_name)
        
        if os.path.isdir(student_path):
            print(f"?? Processing folder: {student_name}...")

            # Process only the first valid image per student
            for img_name in os.listdir(student_path):
                img_path = os.path.join(student_path, img_name)
                
                # Load and encode only the first face image
                try:
                    image = face_recognition.load_image_file(img_path)
                    encoding = face_recognition.face_encodings(image)

                    if encoding:  # Ensure a valid face encoding exists
                        known_face_encodings.append(encoding[0])
                        known_face_names.append(student_name)
                        print(f"? Face added: {student_name} from {img_name}")
                        break  # Stop processing this folder once a face is added

                except Exception as e:
                    print(f"? Error processing {img_name}: {e}")

    print(f"?? Loaded {len(known_face_names)} known faces.")
    return known_face_encodings, known_face_names
