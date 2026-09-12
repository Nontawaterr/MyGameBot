---
title: Overview
type: reference
tags:
- mygamebot
- project
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/project/overview
---

# ภาพรวมโปรเจค

แอป desktop บน Windows เขียนด้วย Python และ CustomTkinter มีแท็บละหนึ่ง [[Project/Glossary|โหมด]]
กด ▶ แล้วบอทจะเปิด thread สแกนหน้าต่างเกมเป็นรอบ ๆ ถ้าเจอปุ่มที่ตรงกับภาพ template ก็จะคลิกแบบเบื้องหลัง
ระหว่างนั้นผู้ใช้ยังใช้คอมพิวเตอร์ทำอย่างอื่นได้

## Stack
- Python 3.10 (`.venv`), ต้องรันบน Windows เท่านั้น เพราะใช้ `pywin32`
- UI: `customtkinter`
- จับภาพและจับคู่ภาพ: `pywin32` (PrintWindow/BitBlt) และ `opencv-python` (`matchTemplate`)
- แพ็กเป็น exe: `pyinstaller` (`--onefile --noconsole`)
- Dev tools: `pytest`, `ruff`

## โครงสร้าง repo
```
main.py              UI + mode registry + scan loops
lib/game_control.py  หา window, จับภาพ, match template, background click
lib/updater.py       auto-update จาก GitHub Releases
lib/version.py       APP_VERSION
config.json          ตั้งค่า runtime + path ของ template
assets/shared/       ภาพที่ใช้ร่วมทุกโหมด
assets/ sougenbi/ realm/ yonder/ even/ draft/   ภาพของแต่ละโหมด
tests/               pytest (ตอนนี้มีแค่ updater)
build.bat  Rubitdd-Bot.spec  make_release.bat
Bitbot/              Obsidian vault นี้
```

## คำสั่งที่ใช้บ่อย
```powershell
.venv\Scripts\python.exe main.py                 # รันแอป
.venv\Scripts\python.exe -m ruff check .         # lint
.venv\Scripts\python.exe -m pytest               # test
.venv\Scripts\python.exe .claude\skills\rubitdd-bot-maintainer\scripts\project_check.py
cmd /c "build.bat < nul"                         # build exe
cmd /c "make_release.bat < nul"                  # zip + release.json
```

## ดูต่อ
- [[Project/Architecture]] · [[Project/Config]] · [[Project/Build and Release]]
- บริบทสำหรับ AI: `CLAUDE.md`, `AGENTS.md`, `CONTEXT.md` ที่ root ของ repo