import os
from flask import Flask, render_template
from flask.wrappers import Response
from camera import VideoRecorder

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
    while recorder:
        data = camera.get_frame()
        frame = data
        if len(frame)==0:
            print("why?")
            break

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