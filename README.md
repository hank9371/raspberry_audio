# 跌倒偵測＋語音對話整合系統

> **硬體**：Raspberry Pi 4B、Logitech C270（含 USB 麥克風）  
> **後端**：Ubuntu 22.04 虛擬機（Xeon E5 CPU-only）  
> **網路**：Tailscale 私有 VPN

---

## 目錄
1. [系統架構](#系統架構)
2. [目錄結構](#目錄結構)
3. [先決套件](#先決套件)
4. [安裝步驟](#安裝步驟)
5. [執行方式](#執行方式)
6. [API 端點](#api-端點)
7. [常見問題](#常見問題)

---

## 系統架構


| 區域 | 角色 | 主要腳本 | 功能 |
|------|------|---------|------|
| Raspberry Pi | `sender.py` | 透過 socket 傳送 C270 影像幀 |
| | `audio_client.py` | 錄音→上傳→接收 TTS→喇叭播放＋字幕列印 |
| Ubuntu VM | `backend_server.py` | 接收影像→`fall_detection.py` 判斷跌倒 |
| | `fall_detection.py` | YOLO v8 + MediaPipe Pose 計算跌倒分數 |
| | `audio_api.py` | Whisper STT → FastSpeech 2 TTS<br>文字清洗、語言偵測、備援音檔、字幕 API |

---

## 目錄結構


