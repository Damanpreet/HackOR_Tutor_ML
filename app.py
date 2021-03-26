import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/video1')
def video1():
	return render_template('video1.html')

@app.route('/video2') 
def video2():
	return render_template('video2.html')

@app.route('/video3')  
def video3():  
	return render_template('video3.html')    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)