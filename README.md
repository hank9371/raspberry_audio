架構說明
左側：Raspberry Pi 4B（Edge 裝置）

C270 USB 攝影機 → sender.py 取流，經 Tailscale 網路送到後端

USB 麥克風 → audio_client.py 錄音

3.5 mm 喇叭 + PAM8403 ← audio_client.py 播放後端回傳的 TTS

本地同時執行 sender.py 與 audio_client.py

右側：Ubuntu VM Backend

backend_server.py：接收影像、呼叫 fall_detection.py 判斷跌倒

audio_api.py（本次改寫）：

faster-whisper → STT

FastSpeech 2（Coqui TTS）→ TTS

文字清洗、語言偵測、備援音檔

/tts_text API 供字幕查詢

其餘推論（Gemma 3 回應文字）可後續插入

資料流

Video stream：Pi → VM；VM 分析後可回前端狀態

Audio upload：Pi → /upload_audio；VM 辨識 + 合成

TTS response：VM → Pi；Pi 播放並在終端列印字幕

全通訊透過 Tailscale 私網
