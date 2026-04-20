# Realtime Object Detector

WebカメラとAIを組み合わせたリアルタイム物体検出システムです。  
YOLOv8による高速な物体検出と、Azure Computer Visionによる詳細な画像分析を組み合わせ、Flaskで構築したWebUIでリアルタイムに結果を確認できます。

---

## 機能

- WebカメラのリアルタイムMJPEGストリーミング表示
- YOLOv8（nanoモデル）による常時物体検出・バウンディングボックス描画
- 検出物体が変化したタイミングでAzure Computer Visionによる自動分析
- 検出結果・Azure分析結果をWebUI上でリアルタイム表示

---

## 使用技術

| 役割 | 技術 |
|---|---|
| Webフレームワーク | Flask |
| リアルタイム物体検出 | YOLOv8n（Ultralytics） |
| 詳細画像分析 | Azure Computer Vision |
| 映像配信 | MJPEG Streaming |
| カメラ取得 | OpenCV |

---

## 動作環境

- Mac（Apple Silicon）
- Python 3.10 以上

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/futosawaguchi/realtime-object-detector.git
cd realtime-object-detector
```

### 2. 仮想環境を作成・有効化

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

`.env.example` をコピーして `.env` を作成し、Azureの情報を記入します。

```bash
cp .env.example .env
```

`.env` を編集：


```bash
AZURE_CV_ENDPOINT=your_azure_endpoint_here
AZURE_CV_API_KEY=your_azure_api_key_here
```

Azure Computer VisionのエンドポイントとAPIキーは、Azure Portal の「キーとエンドポイント」から取得できます。

### 5. 起動

```bash
python app.py
```

ブラウザで `http://127.0.0.1:5000` を開いてください。

---

## ファイル構成

```
realtime-object-detector/
├── app.py               # Flask本体・ルーティング・MJPEGストリーム配信
├── camera.py            # Webカメラの起動・フレーム取得（スレッド管理）
├── detector.py          # YOLOv8による物体検出・バウンディングボックス描画
├── azure_client.py      # Azure Computer Vision APIの非同期呼び出し
├── config.py            # モデル名・閾値・APIキーなどの設定値
├── templates/
│   └── index.html       # WebUI（カメラ映像・検出リスト・Azure結果）
├── static/
│   └── style.css        # スタイルシート
├── .env.example         # 環境変数のテンプレート
└── requirements.txt     # 依存ライブラリ一覧
```

## YOLOモデルの変更方法

`config.py` の1行を変えるだけで精度と速度を切り替えられます。

```python
YOLO_MODEL = "yolov8n.pt"  # nano（高速）
# YOLO_MODEL = "yolov8s.pt"  # small（バランス型）
# YOLO_MODEL = "yolov8m.pt"  # medium（高精度）
```

---

## 注意事項

- `.env` ファイルはGitで管理されません。APIキーを外部に公開しないよう注意してください。
- YOLOv8のモデルファイル（`.pt`）は初回起動時に自動でダウンロードされます。
- Azure Computer Vision APIの利用には、Azureアカウントとリソースの作成が必要です。