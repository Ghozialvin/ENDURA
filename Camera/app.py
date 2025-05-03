from flask import Flask, render_template, Response
import cv2
import PoseModule as pm
import numpy as np

app = Flask(__name__)
cap = cv2.VideoCapture(0)
detector = pm.poseDetector()

count = 0
direction = 0
form = 0

def gen_frames():
    global count, direction, form
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            img = detector.findPose(img, False)
            lmList = detector.findPosition(img, False)
            if len(lmList) != 0:
                elbow = detector.findAngle(img, 11, 13, 15)
                shoulder = detector.findAngle(img, 13, 11, 23)
                hip = detector.findAngle(img, 11, 23, 25)
                per = np.interp(elbow, (90, 160), (0, 100))
                bar = np.interp(elbow, (90, 160), (380, 50))

                feedback, count, direction, form = update_feedback_and_count(
                    elbow, shoulder, hip, direction, count, form)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def update_feedback_and_count(elbow, shoulder, hip, direction, count, form):
    """ Copy dari Push-Up script kamu """
    feedback = "Fix Form"
    if elbow > 160 and shoulder > 40 and hip > 160:
        form = 1
    if form == 1:
        if elbow <= 90 and hip > 160:
            feedback = "Up"
            if direction == 0:
                count += 0.5
                direction = 1
        elif elbow > 160 and shoulder > 40 and hip > 160:
            feedback = "Down"
            if direction == 1:
                count += 0.5
                direction = 0
        else:
            feedback = "Fix Form"
    return feedback, count, direction, form

@app.route('/')
def index():
    return render_template('Push-Upz.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
