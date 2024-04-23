import cv2
import numpy as np
import mss
from flask import Flask, render_template, Response

app = Flask(__name__)

# 设置屏幕捕获的分辨率选项
resolutions = {
    "低清晰度": (640, 480),
    "中等清晰度": (1280, 720),
    "高清晰度": (1920, 1080)
}

# 当前选择的分辨率
current_resolution = "中等清晰度"


def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        while True:
            img = np.array(sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 根据当前选择的分辨率调整图像大小
            width, height = resolutions[current_resolution]
            img = cv2.resize(img, (width, height))

            ret, jpeg = cv2.imencode('.jpg', img)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html', resolutions=resolutions.keys())


@app.route('/video_feed')
def video_feed():
    return Response(capture_screen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_resolution/<resolution>')
def set_resolution(resolution):
    global current_resolution
    if resolution in resolutions:
        current_resolution = resolution
    return "OK"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
