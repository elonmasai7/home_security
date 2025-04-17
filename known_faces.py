import face_recognition
import pickle

def register_known_faces():
    known_encodings = {}
    
    # Example: Register "John Doe"
    image = face_recognition.load_image_file("john.jpg")
    encoding = face_recognition.face_encodings(image)[0]
    known_encodings["John Doe"] = encoding
    
    # Add more people as needed
    
    with open("known_faces.pkl", "wb") as f:
        pickle.dump(known_encodings, f)

register_known_faces()