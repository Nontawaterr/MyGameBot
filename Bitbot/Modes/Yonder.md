---
title: Yonder
type: mode
tags:
- mygamebot
- mode
- yonder
created: 2026-09-11
updated: 2026-09-11
permalink: bitbot/modes/yonder
---

# โหมด yonder

- **แท็บ:** `yonder`
- **Loop:** `_run_yonder` (`main.py:364`)
- **Config section:** `yonder_templates`
- **Threshold:** `confidence_threshold` (0.6)

## Templates
| Key | ไฟล์ | ที่มา |
| --- | --- | --- |
| accept, dismiss, done1, donee | `assets/shared/*.png` | shared |
| challenge | `yonder/challenge.jpg` | yonder (**ไฟล์ .jpg** ตัวเดียวในโปรเจค) |
| continue | `yonder/continue.png` | yonder |
| clear | `yonder/clear.png` | yonder |

## Flow
- ตอนเริ่ม ถ้าไม่มี key `challenge` จะ log `✗ ไม่พบ yonder_templates.challenge` แล้วหยุด
- หลังจากนั้นทำงานเหมือน generic loop คือกดทุกปุ่มที่เจอตามลำดับ

## Template notes
- `challenge.jpg` บีบอัดแบบ lossy อาจทำให้ score ต่ำกว่าภาพ png ถ้ามีปัญหาให้จับภาพใหม่เป็น png