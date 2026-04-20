import cv2
import time
import threading
from flask import Flask, render_template, Response, jsonify

import config
from camera import Camera
from detector import Detector
from azure_client import AzureClient

app = Flask(__name__)

# --- 各モジュールの初期化 ---
camera = Camera(config.CAMERA_INDEX)
detector = Detector()
azure_client = AzureClient()

# --- 共有データ ---
latest_detections: list[dict] = []
detections_lock = threading.Lock()


def generate_frames():
    """MJPEGストリーム用のフレームを生成し続けるジェネレータ"""
    global latest_detections

    camera.start()

    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        # YOLOv8で物体検出
        annotated_frame, detections, changed = detector.detect(frame)

        # 検出結果を共有データに保存
        with detections_lock:
            latest_detections = detections

        # 検出物体が変化したらAzure分析をトリガー
        if changed:
            azure_client.analyze_async(annotated_frame)

        # JPEGエンコードしてMJPEGとして送出
        ret, buffer = cv2.imencode(".jpg", annotated_frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )


# --- ルーティング ---

@app.route("/")
def index():
    """メインページ"""
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """MJPEGストリームのエンドポイント"""
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/detections")
def api_detections():
    """YOLO検出結果をJSON形式で返すエンドポイント"""
    with detections_lock:
        data = latest_detections.copy()
    return jsonify(data)


@app.route("/api/azure")
def api_azure():
    """Azure分析結果をJSON形式で返すエンドポイント"""
    result = azure_client.get_latest_result()
    return jsonify(result or {})


if __name__ == "__main__":
    app.run(debug=False, threaded=True)