# Raspberry Pi ↔ Ubuntu VM 語音 + 跌倒偵測系統

> - **Edge**：Raspberry Pi 4B  
> - **Backend**：Ubuntu VM (CPU-only, Xeon E5)  
> - **Network**：Tailscale VPN

## 目錄結構

```text
project/
├─ pi/                      # Raspberry Pi
│  ├─ sender.py             # 影像送出
│  └─ audio_client.py       # 錄音→上傳→播放→顯示字幕
└─ server/                  # Ubuntu VM
   ├─ audio_api.py          # 語音 API（Whisper + FastSpeech2 + 字幕）
   ├─ backend_server.py     # 影像 Socket + Flask MJPEG
   └─ fall_detection.py     # YOLOv8 + MediaPipe 跌倒判斷
ˋˋˋ
ˋˋˋ
## 功能清單
- **影像串流**：Pi 端攝影機 → Socket → Flask `/video_feed`
- **跌倒偵測**：YOLOv8n + MediaPipe Pose，滑動窗口平滑
- **語音回路**  
  1. Pi 錄音 5 s  
  2. Ubuntu `faster-whisper` 辨識  
  3. 固定/LLM 回應文字 → **文字清洗**  
  4. 中、英以外直接備援；中文走 **FastSpeech2** 合成  
  5. Pi 播放 TTS 並列印字幕
- **字幕 API**：`GET /tts_text` 取最新回應文字
- **視覺化日誌**：`tts_logs.jsonl` 一行一筆 JSON，含時間 / 成功 / 合成秒數
ˋˋˋ
---
