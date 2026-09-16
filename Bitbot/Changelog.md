---
title: Changelog
type: changelog
tags:
- mygamebot
- release
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/changelog
---

# Changelog

สร้างจาก `git log` ใหม่สุดอยู่บน

## 1.0.9 (2026-09-17)
- โหมด [[Modes/Even|even]] แยกเป็น sub-mode Farm / Activity เลือกด้วยปุ่มเหนือบรรทัดสถานะ (`0f10793`)

## 1.0.8 (2026-09-15)
- โหมด [[Modes/Draft|draft]] เจอ `draft-best` แล้วกดตรงกลางภาพ แทนการกดพื้นที่ว่างใต้ภาพ และใช้รูปที่ crop ใหม่เหลือแค่ "Best of All" (`fb7fae9`)
- เพิ่มแท็บ bondling พร้อมตัวเลือกย่อย ฟาม / จับ (หน้า UI อย่างเดียว) (`eff3b51`)
- แก้ ruff ใน `lib/game_control.py` (`579d2f8`)

## 1.0.7 (2026-09-13)
- แก้หน้าต่างค้างระหว่างอัปเดต: งาน network และไฟล์ย้ายไป worker thread และมีหน้าต่าง progress ([[Known Issues]] ข้อ 12)
- ลบโฟลเดอร์ temp ของอัปเดตที่ล้มเหลวหรือถูกปิดกลางทาง ([[Known Issues]] ข้อ 13) (`08a5c1c`) ดู [[Sessions/2026-09-13 แก้อัปเดตค้างและ temp รั่ว]]

## 1.0.6 (2026-09-13)
- แก้เครื่องอื่นอัปเดตอัตโนมัติไม่ได้ (bridge release): zip ใช้ชื่อ `Rubitdd-Bot-update.exe`, แอปเปลี่ยนชื่อกลับเอง, `restart.ps1` retry การคัดลอกและแจ้ง error (`642e34e`) ดู [[Sessions/2026-09-13 Bridge release แก้อัปเดต]]

## 1.0.5 (2026-09-13)
- เพิ่มโหมด [[Modes/Draft|draft]] (`79d8332`)

## 1.0.4 (2026-09-11)
- แก้บั๊กโหมด [[Modes/Even|even]] ค้างเมื่อคลิกพลาด: เลิกจำ step แล้วเช็คตามลำดับใหม่ทุกรอบ (`95ca627`)

## 1.0.3 (2026-09-10)
- ปรับโหมด [[Modes/Even|even]] ให้กดตามลำดับ even-1 → even-2 → continue-1/2 (`fb75b38`)

## 1.0.2 (2026-09-10)
- เพิ่มโหมด [[Modes/Even|even]] (`cd6d025`, 2026-09-09)
- เพิ่มปุ่ม continue ในโหมด even (`a715d38`)

## 1.0.1 (2026-06-01)
- ปรับ [[Modes/Realm|ตีเขต]] (`da8ab84`, 2026-05-31)
- แก้บัคตีเขตไม่ได้ (`3954a2c`)

## 1.0.0 และก่อนหน้า (2026-05-06 – 2026-05-31)
- Updete v1 (`e6e254f`, 2026-05-06)
- เริ่ม v1 (`1514ad9`, 2026-05-30)
- เพิ่มรับเควส (`6a233e1`)
- Remove AI files from repository (`9aaf857`)
- ปรับการฟาม (`8b43043`)
- `make_release.bat` เปลี่ยนมา hash ไฟล์ zip แทน exe และ GUI แสดงก่อนเช็คอัปเดตผ่าน `root.after()` (จากโน้ตเก่าใน `.memory/`)