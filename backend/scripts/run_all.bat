@echo off
echo ==========================================
echo NeuroScrape — Full Pipeline Setup & Launch
echo ==========================================

cd /d "%~dp0\.."

echo 1. Generating NeuroAnchor dataset...
python scripts/build_dataset.py

echo 2. Exporting and quantizing ONNX NeuroAnchor model...
python scripts/quantize_model.py

echo 3. Training Karma quality head...
python scripts/train_karma_head.py

echo 4. Starting NeuroScrape FastAPI Server...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
