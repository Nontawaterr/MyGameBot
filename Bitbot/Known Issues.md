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

### ~~11. เครื่องอื่นอัปเดตไม่ได้: คัดลอกไฟล์ทับตอนที่ .exe ยังถูกล็อก~~ ✅ แก้แล้ว 2026-09-13 (v1.0.6)
- **แก้แล้ว:** zip ใช้ชื่อ `Rubitdd-Bot-update.exe`, `migrate_update_exe_name` เปลี่ยนชื่อกลับตอนเปิด, `restart.ps1` retry การคัดลอก 60 วินาทีและแจ้ง error ทดสอบผ่านรวมถึง v1.0.5 ตัวจริงจาก GitHub → v1.0.6 ดู [[Sessions/2026-09-13 Bridge release แก้อัปเดต]] (รายละเอียดด้านล่างเป็นบันทึกเดิมก่อนแก้ เลขบรรทัดอาจเลื่อนแล้ว)
- .exe แบบ onefile ของ PyInstaller รันเป็น 2 process คือ bootloader (ตัวแม่) กับ python (ตัวลูก) และ `os.getpid()` ที่ส่งให้ `restart.ps1` (`updater.py:333`) เป็น PID ของตัวลูก
- `restart.ps1` รอแค่ตัวลูกปิด (`updater.py:205`) แล้วคัดลอกทับทันที (`updater.py:211-213`) แต่ตอนนั้น bootloader ยังเปิดอยู่ (กำลังลบโฟลเดอร์ `_MEI`) และล็อกไฟล์ .exe ไว้
- `Copy-Item` ล้มเหลวแบบ non-terminating สคริปต์ทำต่อจนจบและลบไฟล์อัปเดตที่โหลดมาทิ้ง (`updater.py:220`) ทดสอบกับ `restart.ps1` ตัวจริงแล้ว แอปปิดไปเฉยๆ ไม่มีตัวไหนเปิดขึ้นมาใหม่
- **สถานการณ์:** กด Yes อัปเดต → แอปปิดไป → ผู้ใช้เปิดเองก็ยังเป็นเวอร์ชันเดิม และถูกถามให้อัปเดตอีก วนไม่จบ
- **ทดสอบ 2026-09-13:** จำลองขั้นติดตั้งด้วย .exe จริง logic เดิมล้มเหลว 3/3 รอบ (`The process cannot access the file ... because it is being used by another process`) ถ้ารอ bootloader ปิดก่อนคัดลอก ผ่าน 2/2 รอบ
- **แนวทางแก้:** ส่ง PID ของ bootloader (`os.getppid()` ตอน frozen) ให้สคริปต์รอด้วย, retry การคัดลอกจนสำเร็จโดยมี timeout, และถ้าคัดลอกไม่สำเร็จห้ามเปิดเวอร์ชันเดิมแบบเงียบๆ
- **เครื่องที่ติดเวอร์ชันเก่า:** รัน `restart.ps1` ตัวเก่าที่ฝังอยู่ใน .exe ของตัวเอง ตัวแก้จึงช่วยตรงๆ ไม่ได้ ทางออกมี 2 ทาง
  - ดาวน์โหลด zip มาแตกทับเองหนึ่งครั้ง
  - **Bridge release (ทดสอบ 2026-09-13 ผ่าน):** ถ้า .exe ใน zip ใช้ **ชื่ออื่น** เช่น `Rubitdd-Bot-bridge.exe` ไฟล์ไม่ชนกับตัวที่ล็อกอยู่ สคริปต์ตัวเก่าคัดลอกผ่าน `_find_launch_executable` เลือกตัวใหม่ (`updater.py:177`) เปิดตัวใหม่ให้เอง และลบไฟล์ staging ครบ แต่ `Rubitdd-Bot.exe` ตัวเก่าจะค้างอยู่ในโฟลเดอร์ ต้องมีขั้นเก็บกวาดหรือเปลี่ยนชื่อกลับในเวอร์ชันนั้น

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

### ~~12. หน้าต่างค้างระหว่างดาวน์โหลดอัปเดต~~ ✅ แก้แล้ว 2026-09-13 (v1.0.7)
- **แก้แล้ว:** `start_update_check` ทำงาน network และไฟล์บน worker thread และมีหน้าต่าง progress ทดสอบแล้วหน้าต่างตอบสนอง 30/30 ครั้งระหว่างดาวน์โหลด ดู [[Sessions/2026-09-13 แก้อัปเดตค้างและ temp รั่ว]]
- (บันทึกเดิมก่อนแก้) `maybe_run_update` ถูกเรียกผ่าน `root.after` บน main thread ของ Tk (`main.py:547`) และ `download_file` (`updater.py:321`) โหลด zip ~60MB แบบบล็อก ไม่มี progress
- **สถานการณ์:** กด Yes แล้วหน้าต่างขึ้น Not Responding จนโหลดเสร็จ ผู้ใช้อาจคิดว่าแฮงค์แล้วปิดทิ้ง

### ~~13. โฟลเดอร์ temp ของอัปเดตรั่วเมื่อล้มเหลว~~ ✅ แก้แล้ว 2026-09-13 (v1.0.7)
- **แก้แล้ว:** `_stage_and_launch_update` ลบโฟลเดอร์ staging ทุกครั้งที่ล้มเหลว และ `_remove_stale_update_dirs` ลบโฟลเดอร์ที่ค้างเกิน 1 ชั่วโมงตอนเช็คอัปเดต ทดสอบ hash ไม่ตรงแล้วไม่มีโฟลเดอร์ค้าง
- (บันทึกเดิมก่อนแก้)
- `stage_root` (`updater.py:317`) ถูกลบเฉพาะใน `restart.ps1` ตอนอัปเดตสำเร็จ ถ้า error ก่อนถึง `_launch_restart_helper` (โหลดขาด, hash ไม่ตรง, หา .exe ไม่เจอ) จะเหลือไฟล์ ~60MB ค้างใน `%TEMP%` ทุกครั้ง

## ⚪ เล็กน้อย / เครื่องมือ
- 7. `build.bat` และ `make_release.bat` จบด้วย `pause` และใช้ `python`/`pyinstaller` จาก PATH ไม่ใช่ `.venv`
- 8. `project_check.py` ฝั่ง `.codex` เช็คแค่ `assets`, `sougenbi`, `realm` (ไม่มี `yonder`, `even`) ฝั่ง `.claude` แก้แล้ว
- 9. หลายโหมดรันพร้อมกันได้และใช้ `GameControl` ร่วมกัน คลิกอาจสลับกันเอง (อาจตั้งใจให้เป็นแบบนี้)
- 10. `GameControl.click()` (foreground) ไม่มีโค้ดส่วนไหนเรียกใช้