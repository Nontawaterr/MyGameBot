---
title: Bondling
type: mode
tags:
- mygamebot
- mode
- bondling
created: 2026-09-13
updated: 2026-09-13
permalink: bitbot/modes/bondling
---

# โหมด bondling

- **แท็บ:** `bondling` (แท็บที่ 7 แท็บสุดท้าย)
- **Loop:** `_run_bondling` (`main.py`) ยังไม่มีการทำงานจริง
- **Config section:** ยังไม่มี (`bondling_templates` ยังไม่ได้เพิ่ม และยังไม่อยู่ใน `MODE_TEMPLATE_KEYS`)
- **Threshold:** -
- **รูปแบบ:** มีตัวเลือกย่อย 2 แบบ ยังไม่ได้ออกแบบ loop

## ตัวเลือกย่อย
อยู่ด้านบนของบรรทัดสถานะ เป็น `CTkSegmentedButton` ค่ามาจาก `BONDLING_SUB_MODES` (`main.py`)

| Key | ปุ่ม | สถานะ |
| --- | --- | --- |
| `farm` | ฟาม | ยังไม่มีการทำงาน (ค่าเริ่มต้น) |
| `catch` | จับ | ยังไม่มีการทำงาน |

## Templates
ยังไม่มี

## Flow ต่อรอบ
ตอนนี้กดเริ่มทำงานแล้วจะ log `✗ Bondling (<ตัวเลือก>) ยังไม่มีการทำงาน` แล้วหยุดเองทันที ค่าตัวเลือกอ่านจาก widget ใน `_get_run_target` (Tk thread) แล้วส่งเข้า worker thread ไม่ได้อ่าน widget จาก worker

## งานที่เหลือเมื่อจะใส่การทำงาน
1. สร้างโฟลเดอร์ `bondling/` และ crop templates
2. เพิ่ม `bondling_templates` ใน `config.json` และ `"bondling": "bondling_templates"` ใน `MODE_TEMPLATE_KEYS`
3. แยก loop ของ ฟาม และ จับ ใน `_run_bondling`
4. เพิ่ม `bondling` ใน `build.bat` และ `Rubitdd-Bot.spec`

## ประวัติ
- 2026-09-13 เพิ่มแท็บ bondling พร้อมตัวเลือกย่อย ฟาม / จับ (หน้า UI อย่างเดียว ยังไม่ได้ release)

## Template notes
-
