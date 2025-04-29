from load_known_faces import get_known_faces

# Load the known faces
known_face_encodings, known_face_names = get_known_faces()

# Print results
print("\n?? Loaded Face Encodings:")
for i, name in enumerate(known_face_names):
    print(f"{i+1}. {name}")
