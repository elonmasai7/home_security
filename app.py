import cv2
import sqlite3
import datetime
import face_recognition
import pickle
import numpy as np
from imutils.video import VideoStream
from imutils.object_detection import non_max_suppression
import imutils
import time

# Load known faces
try:
    with open("known_faces.pkl", "rb") as f:
        known_encodings = pickle.load(f)
except FileNotFoundError:
    known_encodings = {}

# Database setup
conn = sqlite3.connect('home_users.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              entry_time TIMESTAMP,
              exit_time TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS movements
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              timestamp TIMESTAMP,
              area TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id))''')

# Initialize person detector
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Initialize video stream
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Tracking variables
tracked_people = {}
pid_to_name = {}
current_id = 0

def register_face(name, image_path):
    """Function to register new faces"""
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)
    if encoding:
        known_encodings[name] = encoding[0]
        with open("known_faces.pkl", "wb") as f:
            pickle.dump(known_encodings, f)
        return True
    return False

def recognize_face(frame, pid_rect_map):
    """Recognize faces in detected regions"""
    recognized_names = {}
    for pid, (x, y, w, h) in pid_rect_map.items():
        # Extract person region
        person_img = frame[y:y+h, x:x+w]
        rgb_person = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_person)
        if face_locations:
            # Get face encoding
            face_encodings = face_recognition.face_encodings(rgb_person, face_locations)
            if face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    list(known_encodings.values()), face_encodings[0])
                name = "Unknown"
                
                # Use the known face with the smallest distance
                face_distances = face_recognition.face_distance(
                    list(known_encodings.values()), face_encodings[0])
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = list(known_encodings.keys())[best_match_index]
                
                recognized_names[pid] = name
    return recognized_names

def detect_and_track():
    global current_id
    frame = vs.read()
    frame = imutils.resize(frame, width=700)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect people
    (rects, _) = HOGCV.detectMultiScale(rgb_frame, winStride=(4, 4),
                                        padding=(8, 8), scale=1.05)
    rects = non_max_suppression(rects, overlapThresh=0.65)

    # Update tracked people
    current_centroids = {}
    pid_rect_map = {}
    
    for (x, y, w, h) in rects:
        cx = x + w // 2
        cy = y + h // 2
        pid = current_id
        current_centroids[pid] = (cx, cy)
        pid_rect_map[pid] = (x, y, w, h)
        current_id += 1

    # Recognize faces
    recognized_names = recognize_face(frame, pid_rect_map)

    # Update tracking and database
    for pid in list(tracked_people.keys()):
        if pid not in current_centroids:
            # Person exited
            c.execute("UPDATE users SET exit_time = ? WHERE id = ?",
                     (datetime.datetime.now(), pid))
            conn.commit()
            del tracked_people[pid]
            if pid in pid_to_name:
                del pid_to_name[pid]

    for pid in current_centroids:
        if pid not in tracked_people:
            # New person detected
            name = recognized_names.get(pid, f"Unknown {pid}")
            c.execute("INSERT INTO users (name, entry_time) VALUES (?, ?)",
                     (name, datetime.datetime.now()))
            conn.commit()
            tracked_people[pid] = current_centroids[pid]
            pid_to_name[pid] = name

    # Draw annotations
    for pid, (x, y, w, h) in pid_rect_map.items():
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        name = pid_to_name.get(pid, f"Unknown {pid}")
        cv2.putText(frame, name, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Home Monitoring", frame)

try:
    while True:
        detect_and_track()
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
finally:
    cv2.destroyAllWindows()
    vs.stop()
    conn.close()