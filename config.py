import os
from dotenv import load_dotenv

load_dotenv()

# --- Camera ---
CAMERA_INDEX = 0

# --- YOLOv8 ---
YOLO_MODEL = "yolov8n.pt"
YOLO_CONFIDENCE = 0.5

# --- Azure Computer Vision ---
AZURE_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_CV_API_KEY")
AZURE_COOLDOWN_SEC = 3