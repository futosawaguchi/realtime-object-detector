import cv2
import threading


class Camera:
    def __init__(self, camera_index: int):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self._thread = None

    def start(self):
        """カメラのキャプチャをバックグラウンドスレッドで開始"""
        if not self.cap.isOpened():
            raise RuntimeError(f"カメラ (index={self.camera_index}) を開けませんでした")
        self.running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        """常に最新フレームを取得し続けるループ"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        """最新フレームを返す（なければNone）"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """カメラを停止してリソースを解放"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        self.cap.release()