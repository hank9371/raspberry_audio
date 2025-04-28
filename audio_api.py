#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 語音伺服器：
 1. /upload_audio  上傳語音 → Whisper 文字 → TTS 合成 → 回傳 .wav
 2. /tts_text      取得最新回應文字（字幕）
"""

from flask import Flask, request, send_file, jsonify
from faster_whisper import WhisperModel
from TTS.api import TTS
from langdetect import detect
import os, time, json, shutil, re, uuid, logging

app = Flask(__name__)

# ---------- 檔案路徑 ----------
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH   = os.path.join(BASE_DIR, "uploaded.wav")
RESPONSE_PATH = os.path.join(BASE_DIR, "response.wav")
BACKUP_PATH   = os.path.join(BASE_DIR, "backup.wav")        # 請先自備
LOG_PATH      = os.path.join(BASE_DIR, "tts_logs.jsonl")    # 每行一筆 JSON
latest_tts_text = "尚無語音回應"

# ---------- 日誌 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------- 文字清洗 ----------
def clean_text(text: str) -> str:
    """移除 emoji / 奇怪標點，只保留中英文數字與常用標點"""
    text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9，。！？,.!? ]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text or "嗨"

# ---------- 初始化模型 ----------
logging.info("載入 faster-whisper (base/int8, CPU)…")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
logging.info("Whisper 模型就緒")

logging.info("載入 Coqui FastSpeech2 (your_tts)…")
tts = TTS("tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)
logging.info("TTS 模型就緒")

def should_speak(text: str) -> bool:
    """僅當語言偵測為中文才做 TTS，其餘用備援音檔"""
    try:
        return detect(text) in ["zh-cn", "zh-tw"]
    except Exception:
        return False

def log_event(text: str, success: bool, dur: float):
    entry = {
        "id": uuid.uuid4().hex[:8],
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "success": success,
        "duration": round(dur, 2)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ---------- 上傳 + TTS ----------
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    global latest_tts_text
    try:
        # -- 儲存檔案 --
        file = request.files.get("file")
        if not file:
            return "未收到檔案", 400
        file.save(UPLOAD_PATH)

        # -- Whisper 辨識 --
        segments, _ = whisper_model.transcribe(UPLOAD_PATH)
        recognized = "".join([seg.text for seg in segments])
        logging.info(f"Whisper: {recognized}")

        # -- 生成回應文字 (可換 Gemma) --
        response_text = clean_text("你好，我是跌倒偵測系統的小幫手。")
        latest_tts_text = response_text

        # -- 清除舊檔 --
        if os.path.exists(RESPONSE_PATH):
            os.remove(RESPONSE_PATH)

        # -- TTS or 備援 --
        start = time.time()
        if should_speak(response_text):
            tts.tts_to_file(
                text=response_text,
                file_path=RESPONSE_PATH,
                speaker="female-en-2",
                language="zh"
            )
        else:
            shutil.copy(BACKUP_PATH, RESPONSE_PATH)

        # -- 若失敗再用備援 --
        if not os.path.exists(RESPONSE_PATH):
            logging.warning("TTS 失敗，使用備援音檔")
            shutil.copy(BACKUP_PATH, RESPONSE_PATH)

        log_event(response_text, True, time.time() - start)
        return send_file(RESPONSE_PATH, mimetype="audio/wav")

    except Exception as e:
        logging.exception("處理語音時發生例外")
        log_event(str(e), False, 0)
        return f"Server Error: {e}", 500

# ---------- 取得字幕 ----------
@app.route("/tts_text")
def tts_text():
    return jsonify(tts_text=latest_tts_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
