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
latest_annotated_frame = None
detections_lock = threading.Lock()
frame_lock = threading.Lock()


def detection_loop():
    """
    カメラ取得・YOLO推論・Azure送信を専用スレッドで実行
    MJPEGストリームとは完全に分離することでスレッド競合を防ぐ
    """
    global latest_detections, latest_annotated_frame

    camera.start()

    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        # YOLOv8で物体検出
        annotated_frame, detections, changed = detector.detect(frame)

        # 検出結果とフレームを共有データに保存
        with detections_lock:
            latest_detections = detections

        with frame_lock:
            latest_annotated_frame = annotated_frame.copy()

        # 検出物体が変化したらAzure分析をトリガー
        if changed:
            azure_client.analyze_async(annotated_frame)


def generate_frames():
    """
    MJPEGストリーム用ジェネレータ
    detection_loopが用意したフレームを取り出して配信するだけ
    """
    while True:
        with frame_lock:
            frame = latest_annotated_frame
            if frame is not None:
                frame = frame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        ret, buffer = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80]
        )
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

        time.sleep(1 / 30)  # 最大30fps


# --- ルーティング ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/detections")
def api_detections():
    with detections_lock:
        data = latest_detections.copy()
    return jsonify(data)


@app.route("/api/azure")
def api_azure():
    result = azure_client.get_latest_result()
    return jsonify(result or {})


if __name__ == "__main__":
    # 検出ループを専用スレッドで起動
    detection_thread = threading.Thread(
        target=detection_loop, daemon=True
    )
    detection_thread.start()

    app.run(debug=False, threaded=True)