#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspberry Pi 端：
 1. 錄音 (arecord)
 2. 上傳到 /upload_audio
 3. 下載回應音訊並播放 (aplay)
 4. 取得 /tts_text 顯示字幕
"""

import requests, os, time

SERVER_IP      = "100.77.77.70"          # ← 改成 Ubuntu Tailscale IP
UPLOAD_URL     = f"http://{SERVER_IP}:5000/upload_audio"
TTS_TEXT_URL   = f"http://{SERVER_IP}:5000/tts_text"
AUDIO_IN       = "input.wav"
AUDIO_OUT      = "response.wav"
MIC_DEVICE     = "plughw:3,0"            # ← 用 arecord -l 確認

def record(seconds=5):
    print(f"\n🎤 錄音 {seconds}s …")
    cmd = f"arecord -D {MIC_DEVICE} -f cd -t wav -d {seconds} -r 16000 -c 1 {AUDIO_IN}"
    os.system(cmd)

def upload():
    print("📤 上傳語音 …")
    with open(AUDIO_IN, "rb") as f:
        res = requests.post(UPLOAD_URL, files={"file": f})
    if res.status_code == 200:
        with open(AUDIO_OUT, "wb") as out:
            out.write(res.content)
        print("✅ 已取得回應音訊")
        return True
    print(f"❌ 上傳失敗 {res.status_code}")
    return False

def play():
    print("🔊 播放回應 …")
    os.system(f"aplay {AUDIO_OUT}")

def fetch_subtitle():
    try:
        res = requests.get(TTS_TEXT_URL, timeout=2)
        if res.status_code == 200:
            return res.json().get("tts_text", "")
    except Exception:
        pass
    return ""

if __name__ == "__main__":
    while True:
        record(5)
        if upload():
            play()
            print(f"📝 字幕：{fetch_subtitle()}")
        time.sleep(2)
