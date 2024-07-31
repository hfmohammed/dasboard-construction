from flask import Flask # type: ignore
from flask_socketio import SocketIO, emit # type: ignore
from ultralytics import YOLO
import cv2 as cv
import base64
import sqlite3
from datetime import datetime

DB_PATH = "video_data.db"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize YOLO model
MODEL = YOLO("yolov8n")
DATA = {}

def connect_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

CONN = connect_db()
CURSOR = CONN.cursor()

def create_table():
    CURSOR.execute("""
        DROP TABLE IF EXISTS videoData;
    """)
    
    CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS videoData (
            frame_number INTEGER PRIMARY KEY NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_data TEXT NOT NULL,
            uqCategories TEXT NOT NULL
        );
    """)

    CONN.commit()


def insert_data(frame_number, current_data, uqCategories):
    print('inserting...', frame_number, current_data, uqCategories)

    CURSOR.execute(
        """
        INSERT INTO videoData (frame_number, current_data, uqCategories)
        VALUES (?, ?, ?)
        """,
        (frame_number, str(current_data), str(uqCategories))
    )
    CONN.commit()


def processData(x: dict):
    uqCategories = set()
    for i in x.values():
        ik = i.keys()
        for j in ik:
            if j != 'time':
                uqCategories.add(j)

    return ['time'] + list(uqCategories)

def yolo_annotate(frame):
    results = MODEL(frame)
    return results

def capture_camera(source):
    create_table()

    print("_____DEBUG 2: called capture_camera_____")
    if source == "0":
        source = 0

    cap = cv.VideoCapture(source)
    if not cap.isOpened():
        print("_____DEBUG 3: Error: Unable to open video source._____")
        return
    
    print("_____DEBUG 4: Cap is opened!_____")
    stime = datetime.now()
    frameCount = 1
    while cap.isOpened():
        if frameCount >= 500:
            del DATA[frameCount - 500]

        if source == 0:
            DATA[frameCount] = {
                'time': str(datetime.now().strftime("%H:%M:%S")),
            }
        else:
            DATA[frameCount] = {
                'time': str(datetime.now() - stime).split('.')[0],
            }


        ret, frame = cap.read()
        if not ret:
            print("_____DEBUG 5: Failed to grab frame or end of video reached._____")
            break


        results = MODEL(frame)

        for result in results[0].boxes:
            classId = int(result.cls)
            className = MODEL.names[classId]

            if className not in DATA[frameCount]:
                DATA[frameCount][className] = 0
            DATA[frameCount][className] += 1

            x1, y1, x2, y2 = map(int, result.xyxy[0])
            conf = result.conf[0]

            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv.putText(frame, f'{className} {conf:.2f}', (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

        print("_____DEBUG 6: for loop ended____")
        _, buffer = cv.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        print("_____DEBUG 7: frame is converted to binary_____")
        

        # Emit the frame data and annotated results to the frontend
        uqCategories = processData(DATA)

        socketio.emit('video_frame', {
            'frame': frame_data,
            'current_data': DATA[frameCount],
            'data': DATA,
            'uqCategories': uqCategories,

        })

        insert_data(frameCount, DATA[frameCount], uqCategories)

        # Sleep to reduce the frame rate (optional)
        # socketio.sleep(0.1)
        frameCount += 1

    CURSOR.close()
    CONN.close()
    cap.release()

@app.route('/')
def index():
    return "Server is running"

if __name__ == '__main__':
    source = "../resources/cars.mp4"
    # source = "0"
    print(f"______DEBUG 1: source: {source}______")
    socketio.start_background_task(capture_camera, source)
    socketio.run(app, host='0.0.0.0', port=5001)