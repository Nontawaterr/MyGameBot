---
title: 2026-09-13 Bridge release แก้อัปเดต
type: session
tags:
- session
- updater
- release
created: 2026-09-13
---

# 2026-09-13: Bridge release แก้อัปเดตอัตโนมัติ (v1.0.6)

## เป้าหมาย
ผู้ใช้แจ้งว่าเครื่องอื่นอัปเดตไม่ได้ ต้องหาสาเหตุ แก้ และทำให้เครื่องที่ติดเวอร์ชันเก่าอัปเดตผ่านปุ่ม Yes ได้เอง โดยไม่ต้องให้ทุกคนโหลดใหม่

## สาเหตุ
- .exe แบบ onefile รันเป็น 2 process คือ bootloader กับ python `restart.ps1` รอแค่ process python ปิด แล้วคัดลอกทับ `Rubitdd-Bot.exe` ทันที ตอนนั้น bootloader ยังล็อกไฟล์อยู่ `Copy-Item` จึงล้มเหลวแบบเงียบ แอปปิดไป และไฟล์อัปเดตที่โหลดมาถูกลบ
- จำลองขั้นติดตั้งด้วย .exe จริง: logic เดิมล้มเหลว 3/3 รอบ, รอ bootloader ปิดก่อนผ่าน 2/2 รอบ
- ฝั่งเครือข่ายไม่มีปัญหา: repo public, API ตอบ 200, rate limit ยังเหลือ, updater ไม่เปลี่ยนตั้งแต่ v1.0.1

## สิ่งที่ทำ
- `make_release.bat` ใส่ .exe ใน zip ในชื่อ `Rubitdd-Bot-update.exe` สคริปต์ของ 1.0.0–1.0.5 จึงคัดลอกผ่านเพราะชื่อไม่ชนกับไฟล์ที่ล็อก และ `_find_launch_executable` เลือกไฟล์นี้เอง
- `migrate_update_exe_name` (`lib/updater.py`) เรียกต้น `main()`: ถ้าเปิดในชื่อ update จะคัดลอกตัวเองทับ `Rubitdd-Bot.exe` (retry) แล้วเปิดใหม่และออก ถ้าเปิดในชื่อปกติแล้วมีไฟล์ชื่อ update ค้าง จะลบใน background (retry)
- `restart.ps1` ใหม่: `$ErrorActionPreference = 'Stop'`, retry การคัดลอก 60 วินาที, ถ้าไม่ผ่านแสดง MessageBox แทนการเงียบ
- เปิด .exe ตัวใหม่ด้วย `PYINSTALLER_RESET_ENVIRONMENT=1`
- เพิ่ม `tests/test_update_exe_name.py` (4 tests)
- **ข้อตกลง:** ทุก release ต่อจากนี้ต้องใช้ชื่อ `Rubitdd-Bot-update.exe` ใน zip เพราะเครื่องที่ยังไม่เคยผ่าน 1.0.6 จะกระโดดไป release ล่าสุดทันที

## ไฟล์ที่แก้
- `lib/updater.py`: `CANONICAL_EXE_NAME`, `UPDATE_EXE_NAME`, `restart.ps1`, `_fresh_app_env`, `_copy_with_retry`, `_remove_with_retry`, `migrate_update_exe_name`
- `main.py`: เรียก `migrate_update_exe_name()` ต้น `main()`
- `make_release.bat`: zip ด้วยชื่อ `Rubitdd-Bot-update.exe`
- commits `642e34e`, `0119e38` และ GitHub Release `v1.0.6`

## ผลการตรวจ
- ruff: ไฟล์ที่แก้ผ่าน
- pytest: 13 passed
- project_check: ผ่าน
- E2E 1: v1.0.5 (build จาก tag ชี้ server จำลอง) → 1.0.6 ✅ ~15 วินาที
- E2E 2: updater ใหม่ 1.0.6 → 1.0.7 จำลองที่ zip ใช้ชื่อเดิม ต้องผ่านการล็อกด้วย retry ✅
- E2E 3: **v1.0.5 ตัวจริงจาก GitHub → v1.0.6 บน GitHub** ✅ ~38 วินาที (ดาวน์โหลดราว 23 วินาที) ไม่มีไฟล์ค้างในโฟลเดอร์หรือ `%TEMP%`
- ทดสอบกับเกมจริง: ไม่เกี่ยว (เปลี่ยนแค่ updater)

## พบระหว่างทาง
- [[Known Issues]] ข้อ 12 (หน้าต่างค้างระหว่างดาวน์โหลด ไม่มี progress เห็นช่วงดาวน์โหลดราว 23 วินาทีใน E2E 3) และข้อ 13 (โฟลเดอร์ temp รั่วเมื่ออัปเดตล้มเหลว) ยังไม่แก้
- ถ้าผู้ใช้เปลี่ยนชื่อ .exe ของตัวเองเป็นชื่ออื่น ไฟล์ชื่อนั้นจะไม่ถูกแทน เวอร์ชันใหม่จะไปอยู่ที่ `Rubitdd-Bot.exe`

## ต่อไป
- [ ] แก้ Known Issues 12 และ 13
- [ ] ถ้าแก้ `make_release.bat` ห้ามเอาการเปลี่ยนชื่อเป็น `Rubitdd-Bot-update.exe` ออก
