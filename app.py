import os
from flask import Flask, render_template
from flask.wrappers import Response
from camera import VideoRecorder
from .processing import calculate_scores

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT']=0

global recorder
recorder = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

def gen(camera):
    global recorder
    # Blink initializations
    blink_counter, total_blinks = 0, 0
    # Yawn initializations
    yawn_counter, total_yawns = 0, 0

    frames = 0

    while recorder:
        frame = camera.get_frame()
        frames += 1
        if len(frame)==0:
            print("why??")
            break
        blinking, yawning, ear, lar = calculate_scores(frame)
        if blinking:
            blink_counter += 1
        else:
            if blink_counter > 8:
                total_blinks += 1
            blink_counter = 0

        if yawning:
            yawn_counter += 1
        else:
            if yawn_counter > 1:
                total_yawns += 1


@app.route('/video_feed')
def video_feed():
    global recorder
    recorder = VideoRecorder()
    gen(recorder)
    return {}

@app.route('/video_stop')
def video_stop():
    global recorder
    del recorder
    recorder = None
    print("resource released!")
    return {}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
