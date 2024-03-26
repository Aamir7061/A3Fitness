from flask import Flask,session, render_template, Response, redirect, url_for,jsonify,request
import cv2
import mediapipe as mp
import numpy as np
import math
app = Flask(__name__)
app.secret_key = '@amir'  
#Global Variables
users = {}
total_exer={}
exercise_type=None
monitoring = False
replication_count = 0
status = None
total_time=0
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence = 0.65, min_tracking_confidence = 0.75)
cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    global cap
    if cap is not None:
        cap.release()  
        cap = None 
    username = session.get('username')
    return render_template('app.html', username=username)
@app.route('/home')
def home():
    global cap
    if cap is not None:
        cap.release() 
        cap = None
    if 'username' in session:
        return render_template('app.html', username=session['username'])
    return render_template('app.html')
@app.route('/bmi-checker')
def bmichecker():    
    return render_template('bmi-checker.html')

@app.route('/about')
def about():    
    return render_template('about.html')
    
@app.route('/turn_off_camera', methods=['POST'])
def turn_off_camera():
    global cap
    if cap is not None:
        cap.release()  
        cap = None     
    return 'Camera turned off'

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'})
    else:
        users[username] = password
        return jsonify({'success': True, 'message': 'Sign up successful'})

@app.route('/login', methods=['POST'])
def login():
    global total_time
    total_time=0
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        session['username'] = username  
        return jsonify({'success': True, 'message': 'Login successful', 'username': username})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global total_time
    total_time=0
    session.clear()
    return redirect(url_for('home'))

# Function for Calculating the angle
def calculate_angle(a,b,c):
    a = np.array(a) 
    b = np.array(b) 
    c = np.array(c) 
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle >180.0:
        angle = 360-angle
    return angle


def jumping_jacks(image):
    try:
        global replication_count,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)        
        landmarks = results.pose_landmarks.landmark
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_hip_visible = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > 0.75
        right_hip_visible = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility > 0.75
        hipr = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        angle = calculate_angle(hip,shoulder, elbow)
        angle1 = calculate_angle(hipr,hip, knee)            
        cv2.putText(image, str(int(angle)),
                tuple(np.multiply(shoulder, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        cv2.putText(image, str(int(angle1)),
                tuple(np.multiply(hipr, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 225), 2, cv2.LINE_AA)
        if left_hip_visible or right_hip_visible:
            if angle < 30 and status==None and angle1<95:
                status = 'True'
            if status == 'True' and angle > 120 and angle1>105:
                status = 'False'
            if status =='False' and angle<30 and angle1<95:
                status = 'True'
                replication_count = replication_count + 1
                        
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")
    return image


def pullup(image):
    try:
        global replication_count,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)        
        landmarks = results.pose_landmarks.landmark
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_elbow_visible = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility > 0.75
        right_elbow_visible = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility > 0.75
        angle = calculate_angle(shoulder, elbow, wrist)
        cv2.putText(image, str(int(angle)),
                tuple(np.multiply(elbow, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        if left_elbow_visible or right_elbow_visible:
            if angle > 160 and status==None:
                status = 'True'
            if status == 'True' and angle < 75:
                status = 'False'
            if status =='False' and angle>110:
                status = 'True'
                replication_count = replication_count + 1
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")
    return image

def pushup(image):
    try:
        global replication_count,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False               
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        landmarks = results.pose_landmarks.landmark 
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_elbow_visible = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility > 0.75
        right_elbow_visible = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility > 0.75
        left_knee_visible = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility > 0.75
        right_knee_visible = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility > 0.75
        left_shoulder_visible = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility > 0.75
        right_shoulder_visible = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility > 0.75
        left_hip_visible = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > 0.75
        right_hip_visible = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility > 0.75
        angle = calculate_angle(shoulder, elbow, wrist)
        cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        if left_elbow_visible or right_elbow_visible and left_hip_visible or right_hip_visible and left_knee_visible or right_knee_visible:   
            if angle < 160 and status==None:
                status = 'True'
            if status == 'True' and angle < 70:
                status = 'False'
            if status =='False' and angle>90:
                status = 'True'
                replication_count = replication_count + 1    
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")    
    return image

def situp(image):
    try:
        global replication_count,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        landmarks = results.pose_landmarks.landmark        
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_knee_visible = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility > 0.75
        right_knee_visible = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility > 0.75
        left_shoulder_visible = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility > 0.75
        right_shoulder_visible = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility > 0.75
        left_hip_visible = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > 0.75
        right_hip_visible = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility > 0.75
        angle = calculate_angle(shoulder,hip, knee)
        cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(hip, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        if left_hip_visible or right_hip_visible and left_knee_visible or right_knee_visible and left_shoulder_visible or right_shoulder_visible:
            if angle < 105 and status==None and len(landmarks)>10:
                status = 'True'
            if status == 'True' and angle < 55:
                status = 'False'
            if status =='False' and angle>70 and len(landmarks)>10:
                status = 'True'
                replication_count = replication_count + 1
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")
    return image

def squats(image):
    try:
        global replication_count,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        landmarks = results.pose_landmarks.landmark        
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        left_hip_visible = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > 0.75
        right_hip_visible = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility > 0.75
        left_ankle_visible = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility > 0.75
        left_knee_visible = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility > 0.75
        right_knee_visible = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility > 0.75
        angle = calculate_angle(hip, knee, ankle)
        cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(knee, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        if left_knee_visible or right_knee_visible and left_hip_visible or right_hip_visible and left_ankle_visible:
            if angle < 160 and status==None:
                status = 'True'
            if status == 'True' and angle < 90:
                status = 'False'
            if status =='False' and angle>110:
                status = 'True'
                replication_count = replication_count + 1
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")
    return image

def biceps(image):
    try:
        global replication_count ,status
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)                
        landmarks = results.pose_landmarks.landmark
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        right_shoulder_visible = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility > 0.75
        shoulder_visible = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility > 0.75
        wrist_visible = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility > 0.75
        right_wrist_visible = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility > 0.75
        left_elbow_visible = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility > 0.75
        right_elbow_visible = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility > 0.75
        angle = calculate_angle(shoulder, elbow, wrist)
        cv2.putText(image, str(int(angle)),
                tuple(np.multiply(elbow, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 155, 55), 2, cv2.LINE_AA)
        if left_elbow_visible or right_elbow_visible and shoulder_visible or right_shoulder_visible and wrist_visible or right_wrist_visible:
            if angle < 160 and status==None and len(landmarks)>16:
                status = 'True'
            if status == 'True' and angle < 45:
                status = 'False'
            if status =='False' and angle>90 and len(landmarks)>16:
                status = 'True'
                replication_count = replication_count + 1
        cv2.putText(image, 'Counter :' + str(replication_count), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        cv2.putText(image, 'Status :' + str(status), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (145, 240, 94), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 120, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 76, 130), thickness=2, circle_radius=2))
    except Exception as e:
        print(f"An error occurred: {e}")
    return image

def generate_frames():
    global monitoring, replication_count,exercise_type
    global cap
    cap = cv2.VideoCapture(0)
    while True:
        ret, image = cap.read()
        if not ret:
            break
        if monitoring:
            if exercise_type=="Pull Ups":
                image=pullup(image)
            if exercise_type=="Push Ups":
                image=pushup(image)
            if exercise_type=="Jumping Jacks":
                image=jumping_jacks(image)
            if exercise_type=="Sit Ups":
                image=situp(image)
            if exercise_type=="Squats":
                image=squats(image)
            if exercise_type=="Biceps":
                image=biceps(image)
        ret, buffer = cv2.imencode('.jpg', image)
        image = buffer.tobytes()
        yield (b'--image\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')


@app.route('/pull_up', methods=['GET', 'POST'])
def pull_up():
    global exercise_type
    exercise_type='Pull Ups' 
    image_path = "/static/images/pul-up.gif"
    if 'username' in session:
        return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)

@app.route('/jumpingjacks', methods=['GET', 'POST'])
def jumpingjacks():
    global exercise_type
    exercise_type='Jumping Jacks' 
    image_path = "/static/images/jump-jacks.gif"
    if 'username' in session:
        return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)

@app.route('/push_up', methods=['GET', 'POST'])
def push_up():
    global exercise_type
    exercise_type='Push Ups'
    image_path = "/static/images/push-up.gif"
    if 'username' in session:
         return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)

@app.route('/sit_up', methods=['GET', 'POST'])
def sit_up():
    global exercise_type
    exercise_type='Sit Ups'
    image_path = "/static/images/sit-up.gif"
    if 'username' in session:
         return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)
@app.route('/squat', methods=['GET', 'POST'])
def squat():
    global exercise_type
    exercise_type='Squats'
    image_path = "/static/images/squat.gif"
    if 'username' in session:
       return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)
@app.route('/bicep', methods=['GET', 'POST'])
def bicep():
    global exercise_type
    exercise_type='Biceps'
    image_path = "/static/images/bicep.gif"
    if 'username' in session:
       return render_template('index.html', username=session['username'],Exercise_Type=exercise_type,image_path=image_path)
    return render_template('index.html',Exercise_Type=exercise_type,image_path=image_path)
    
@app.route('/goto/<page>')
def goto(page):
    if page=='page':
        global exercise_type
        if exercise_type=="Pull Ups":
            return redirect(url_for('push_up'))
        if exercise_type=="Push Ups":
            return redirect(url_for('sit_up'))
        if exercise_type=="Jumping Jacks":
            return redirect(url_for('bicep'))
        if exercise_type=="Sit Ups":
            return redirect(url_for('squat'))
        if exercise_type=="Squats":
            return redirect(url_for('jumpingjacks'))
        if exercise_type=="Biceps":
            return redirect(url_for('finished'))
    return redirect(url_for(page))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=image')

@app.route('/start_monitoring')
def start_monitoring():
    global monitoring
    monitoring = True
    return 'Monitoring started'

@app.route('/stop_monitoring')
def stop_monitoring():
    elapsedTime = int(request.args.get('elapsedTime'))
    hours = math.floor(elapsedTime / 3600000)
    minutes = math.floor((elapsedTime % 3600000) / 60000)
    seconds = math.floor((elapsedTime % 60000) / 1000)
    hours_str = str(hours)
    minutes_str = str(minutes)
    seconds_str = str(seconds)
    a = hours_str + ':' + minutes_str + ':' + seconds_str
    
    global monitoring, replication_count,exercise_type,total_exer, total_time
    total_time+=elapsedTime
    monitoring = False
    count = replication_count
    replication_count = 0
    total_exer[exercise_type]= (count,a)
    print(total_exer)
    return jsonify(number=count, message=exercise_type)



@app.route('/finished')
def finished():
    global cap,total_time
    hours = math.floor(total_time / 3600000)
    minutes = math.floor((total_time % 3600000) / 60000)
    seconds = math.floor((total_time % 60000) / 1000)
    hours_str = str(hours)
    minutes_str = str(minutes)
    seconds_str = str(seconds)
    # Concatenate the strings with the colon ':'
    a = hours_str + 'Hrs:' + minutes_str + 'Min:' + seconds_str+'Sec'
    total_time=0
    if cap is not None:
        cap.release()  
        cap = None 
    global total_exer
    if 'username' in session:
        return render_template('finished.html',username=session['username'], performance_data=total_exer,total_duration='Total Duration : {}'.format(a))
    else:
        return render_template('finished.html',username='Guest', performance_data=total_exer,total_duration='Total Duration : {}'.format(a))

if __name__ == "__main__":
    app.run(debug=True)
