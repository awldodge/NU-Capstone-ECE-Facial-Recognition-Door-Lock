#face_training.py
import os
import cv2
import face_recognition
import pickle
from imutils import paths

image_paths = list(paths.list_images("dataset"))
encodings = []
names = []

for path in image_paths:
    name = os.path.basename(os.path.dirname(path))
    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model="hog")
    faces = face_recognition.face_encodings(rgb, boxes)
    for face in faces:
        encodings.append(face)
        names.append(name)

data = {"encodings": encodings, "names": names}
with open("encodings.pickle", "wb") as f:
    pickle.dump(data, f)
print("Encodings saved to encodings.pickle")
