---
title: Draft
type: mode
tags:
- mygamebot
- mode
- draft
created: 2026-09-13
updated: 2026-09-15
permalink: bitbot/modes/draft
---

# โหมด draft

- **แท็บ:** `draft`
- **Loop:** `_run_draft` (`main.py:480`)
- **Config section:** `draft_templates`
- **Threshold:** `confidence_threshold` (0.6)
- **รูปแบบ:** กฎเฉพาะแบบ stateless (ไม่จำว่ารอบก่อนกดอะไร)

## Templates
| Key | ไฟล์ | บทบาท |
| --- | --- | --- |
| `accept` | `assets/shared/accept.png` (มาจาก shared) | กดตรงกลาง |
| `draft-fight` | `draft/draft-fight.jpg` | ปุ่ม Fight กดตรงกลาง |
| `draft-best` | `draft/draft-best.png` | หน้า Best of All กดตรงกลางภาพ |
| `draft-victory` | `draft/draft-victory.png` | หน้า Victory แค่ log แล้วให้ขั้น `continue` ที่อยู่ถัดไปเป็นคนกด |
| `continue` | `assets/continue.png` (ภาพเดียวกับโหมด soul) | Tap to continue กดตรงกลาง |

ใช้ shared แค่ `accept` ตามที่ผู้ใช้ระบุ ต่างจากโหมดอื่นที่กดครบ 4 ตัว (`dismiss`, `done1`, `donee` ถูก merge เข้ามาใน templates แต่ loop ไม่ได้ใช้)

## Flow ต่อรอบ
1. เจอ `accept` กด
2. เจอ `draft-fight` กด
3. เจอ `draft-best` กดตรงกลางภาพ
4. เจอ `draft-victory` log `✓ พบ Draft-victory - เช็คปุ่ม Continue`
5. เจอ `continue` กด
6. พัก `loop_delay`

หลังคลิกแต่ละครั้งพัก 0.5 วินาที ตอนเริ่มถ้า key ใน `DRAFT_REQUIRED_KEYS` (`main.py:67`) ไม่ครบ จะ log `✗` แล้วหยุด

เหตุที่ไม่จำ step: โหมด [[Modes/Even|even]] เคยจำ step แล้วค้างเมื่อคลิกพลาด (แก้ใน 1.0.4) โหมด draft จึงเช็คทุกปุ่มทุกรอบตั้งแต่แรก

## ประวัติ
- 2026-09-13 เพิ่มโหมด draft (v1.0.5, ยังไม่ได้ทดสอบกับเกมจริง)
- 2026-09-15 `draft-best` เปลี่ยนจากกดพื้นที่ว่างใต้ภาพ 25px เป็นกดตรงกลางภาพ ลบ `DRAFT_BEST_CLICK_OFFSET` และ `GameControl.template_size` (v1.0.8, ยังไม่ได้ทดสอบกับเกมจริง)

## Template notes
- 2026-09-13 `draft-best` เดิม (327×462) มีป้ายชื่อตัวละคร ("Rider") และฉากหลังเคลื่อนไหวติดอยู่ในภาพ เสี่ยงแมตช์ไม่ติดถ้าตัวละครเปลี่ยน
- 2026-09-15 ผู้ใช้ crop `draft-best` ใหม่เหลือ 327×250 เฉพาะตัวอักษร "Best of All" ไม่มีป้ายชื่อตัวละครแล้ว
- 2026-09-13 `draft-victory` (355×178) มีตัวละครฉากหลังติดมา อาจแมตช์ไม่ติดถ้าฉากเปลี่ยน
