import cv2
import json
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace
import os

VIDEO_PATH = "Dataset_Assignment/Video_1/Class_8_cctv_video_1.mov"
OUTPUT_FOLDER = "sample_data"

EMOTION_MAP = {
    "happy": 80,
    "neutral": 70,
    "sad": 40,
    "angry": 35,
    "fear": 30,
    "surprise": 65
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

detector = MTCNN()
cap = cv2.VideoCapture(VIDEO_PATH)

frame_id = 0
frame_skip = 60
face_frames = 0
emotion_scores = []

print("Processing video...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    if frame_id % frame_skip != 0:
        continue

    print(f"Analyzing frame {frame_id}")

    faces = detector.detect_faces(frame)

    if len(faces) > 0:
        face_frames += 1
        try:
            result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
            emotion = result[0]["dominant_emotion"]
            emotion_scores.append(EMOTION_MAP.get(emotion, 60))
        except:
            pass

cap.release()

person_detected = face_frames > 0
wellbeing_score = int(np.mean(emotion_scores)) if emotion_scores else 65

print("Generating daily behavioral data...")

daily_data = [
    {"wellbeing": wellbeing_score, "social": 68, "energy": 60},
    {"wellbeing": wellbeing_score + 3, "social": 70, "energy": 62},
    {"wellbeing": wellbeing_score + 1, "social": 69, "energy": 58},
    {"wellbeing": 48, "social": 40, "energy": 50},
    {"wellbeing": 42, "social": 38, "energy": 45},
]

for i, d in enumerate(daily_data, start=1):
    gaze_direction = "forward" if i < 4 else "downward"
    gaze_contact = True if i < 4 else False

    data = {
        "date": f"day_{i}",
        "person_detected": person_detected,
        "wellbeing": d["wellbeing"],
        "social_engagement": d["social"],
        "energy": d["energy"],
        "gaze_direction": gaze_direction,
        "gaze_contact": gaze_contact
    }

    with open(f"{OUTPUT_FOLDER}/day_{i}.json", "w") as f:
        json.dump(data, f, indent=4)

print("JSON files created in sample_data/")
print(f"Total files: {len(daily_data)}")