import os
import dlib
import time
from collections import defaultdict
from flask import Flask, render_template, request
from camera import VideoRecorder
from processing import analyze_frame
import configparser
import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT']=0

# global configs
global recorder
global blink_counter #, total_blinks
global yawn_counter #, total_yawns
global frameCount
recorder = None

# Blink initializations
blink_counter, yawn_counter = 0, 0
# Yawn initializations
total_blinks, total_yawns = defaultdict(lambda: 0), defaultdict(lambda: 0)
total_drowsiness = defaultdict(lambda: 0)
# read the config file.
cfg = configparser.ConfigParser()
cfg.read('config.INI')

def gen(camera, videoId):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    global recorder, blink_counter, yawn_counter
    # global total_blinks, total_yawns 
    global frameCount
    frameCount = 0
    prev = 0

    while recorder:
        
        time_elapsed = time.time() - prev
        frame = camera.get_frame()

        if time_elapsed < 1/cfg.getint('CAMERA', 'fps'):    # to handle number of frames to be processed in a second.
            print(time_elapsed)
            
            continue
        frameCount += 1
        prev = time.time()

        if len(frame)==0:
            
            print(videoId, frameCount/cfg.getint('CAMERA', 'fps'), total_blinks, total_drowsiness, total_yawns)
            # return videoId, frameCount/cfg.getint('CAMERA', 'fps'), total_blinks, total_drowsiness, total_yawns # assuming cv2 captures 30 frames/sec.
            break

        blinking, yawning = analyze_frame(frame, cfg, detector, predictor)
        
        if blinking:
            blink_counter += 1
        else:
            if blink_counter > cfg.getfloat('YAWN', 'drowsiness_thresh'):
                total_drowsiness[videoId] += 1
            elif blink_counter > cfg.getfloat('YAWN', 'blink_thresh'):
                total_blinks[videoId] += 1
            blink_counter = 0

        if yawning:
            yawn_counter += 1
        else:
            if yawn_counter > cfg.getfloat('YAWN', 'yawn_thresh'):
                total_yawns[videoId] += 1
            yawn_counter = 0


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    try:
        videoId = request.args['id']
    except:
        videoId = 0
    global recorder
    recorder = VideoRecorder()
    gen(recorder, videoId)
    return {}

@app.route('/video_stop', methods=['GET', 'POST'])
def video_stop():
    try:
        videoId = request.args['id']
    except:
        videoId = 0
    global recorder, blink_counter, yawn_counter
    global frameCount
    del recorder
    recorder = None
    blink_counter, yawn_counter = 0, 0
    print("resource released!")

    results = []

    results.append(videoId)
    results.append(frameCount/cfg.getint('CAMERA', 'fps'))
    results.append(total_blinks)
    results.append(total_drowsiness)
    results.append(total_yawns)
 
    print("\n\n")

    for i in results:
        print (i)
    
    print("\n\n")

    # print(videoId, frameCount/cfg.getint('CAMERA', 'fps'), total_blinks, total_drowsiness, total_yawns)
    return render_template('results.html', results = results)

@app.route('/results')
def results():
    return return_template('results.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
