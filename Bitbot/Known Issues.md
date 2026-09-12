---
title: Known Issues
type: issue
tags:
- mygamebot
- bugs
- risks
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/known-issues
---

# Known Issues

พบจากการอ่านโค้ดวันที่ 2026-09-11 (ยังไม่ได้แก้และยังไม่ได้ทดสอบกับเกมจริง)
เมื่อแก้แล้วให้ขีดฆ่า `~~...~~` พร้อมใส่วันที่และลิงก์ session

## 🔴 สำคัญ

### 1. GameControl ค้างหลังปิดหรือเปิดเกมใหม่
- `_ensure_bot()` สร้าง `GameControl` ครั้งเดียวแล้ว cache ไว้ตลอด (`main.py:258`)
- **สถานการณ์:** เปิดบอท → ปิดเกม → เปิดเกมใหม่ → กด ▶ โหมดไหนก็ error `ไม่พบหน้าต่างเกม (Window closed)` ทันที เพราะ `hwnd` เก่าไม่มีแล้ว (`game_control.py:57`) ต้องปิดแอปแล้วเปิดใหม่
- **แนวทางแก้:** ถ้า `not win32gui.IsWindow(self.bot.hwnd)` ให้สร้าง `GameControl` ใหม่

### 2. กดหยุดแล้วเริ่มใหม่เร็ว ๆ อาจมี loop ซ้อนกันสอง thread
- `stop_mode` แค่ตั้ง `running = False` ไม่ได้รอให้ thread จบ (`main.py:231`)
- **สถานการณ์:** กด ■ ตอน thread เก่ากำลัง sleep อยู่ แล้วกด ▶ ทันที → `running` กลับเป็น `True` → thread เก่าตื่นมาทำงานต่อพร้อม thread ใหม่ ทำให้คลิกซ้ำ
- **แนวทางแก้:** ใช้ `threading.Event` แยกต่อ run หรือเก็บ run id แล้วให้ thread เช็คว่าตัวเองยังเป็น run ปัจจุบันอยู่ไหม

## 🟡 ปานกลาง

### 3. Realm ไม่กด shared accept, dismiss, donee
- `_run_realm` เช็คแค่ `done1` จาก shared (`main.py:299`) ถ้ามี popup accept หรือ dismiss โหมด realm จะค้าง
- ต้องถามผู้ใช้ก่อนว่าตั้งใจให้เป็นแบบนี้หรือเปล่า

### 4. ประสิทธิภาพ: จับภาพหน้าจอใหม่ทุก template
- `find_image` เรียก `background_screenshot()` และ `cv2.imread` ทุกครั้งที่เรียก (`game_control.py:114`, `:119`)
- soul ใช้ 7 template = จับภาพ 7 ครั้งต่อรอบ
- **แนวทางแก้:** จับภาพครั้งเดียวต่อรอบ และ cache template ที่โหลดแล้ว

### 5. GDI handle รั่วถ้าเกิด exception ระหว่างจับภาพ
- `background_screenshot` ไม่มี `try/finally` ตอนคืน DC และ bitmap (`game_control.py:69-98`)

### 6. Updater ข้ามการตรวจ hash ถ้า `sha256` ว่าง
- `if manifest.sha256:` (`updater.py:323`) ถ้าอัป `release.json` ที่ไม่มี hash จะติดตั้งโดยไม่ตรวจ

## ⚪ เล็กน้อย / เครื่องมือ
- 7. `build.bat` และ `make_release.bat` จบด้วย `pause` และใช้ `python`/`pyinstaller` จาก PATH ไม่ใช่ `.venv`
- 8. `project_check.py` ฝั่ง `.codex` เช็คแค่ `assets`, `sougenbi`, `realm` (ไม่มี `yonder`, `even`) ฝั่ง `.claude` แก้แล้ว
- 9. หลายโหมดรันพร้อมกันได้และใช้ `GameControl` ร่วมกัน คลิกอาจสลับกันเอง (อาจตั้งใจให้เป็นแบบนี้)
- 10. `GameControl.click()` (foreground) ไม่มีโค้ดส่วนไหนเรียกใช้