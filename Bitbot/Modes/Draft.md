---
title: Draft
type: mode
tags:
- mygamebot
- mode
- draft
created: 2026-09-13
updated: 2026-09-13
permalink: bitbot/modes/draft
---

# โหมด draft

- **แท็บ:** `draft` (แท็บที่ 6 แท็บสุดท้าย)
- **Loop:** `_run_draft` (`main.py:459`)
- **Config section:** `draft_templates`
- **Threshold:** `confidence_threshold` (0.6)
- **รูปแบบ:** กฎเฉพาะแบบ stateless (ไม่จำว่ารอบก่อนกดอะไร) และมี Offset Click ที่ `draft-best`

## Templates
| Key | ไฟล์ | บทบาท |
| --- | --- | --- |
| `accept` | `assets/shared/accept.png` (มาจาก shared) | กดตรงกลาง |
| `draft-fight` | `draft/draft-fight.jpg` | ปุ่ม Fight กดตรงกลาง |
| `draft-best` | `draft/draft-best.png` | หน้า Best of All ไม่มีปุ่ม จึงกดพื้นที่ว่างใต้ขอบล่างของภาพ `DRAFT_BEST_CLICK_OFFSET` = 25px (`main.py:65`) |
| `draft-victory` | `draft/draft-victory.png` | หน้า Victory แค่ log แล้วให้ขั้น `continue` ที่อยู่ถัดไปเป็นคนกด |
| `continue` | `assets/continue.png` (ภาพเดียวกับโหมด soul) | Tap to continue กดตรงกลาง |

ใช้ shared แค่ `accept` ตามที่ผู้ใช้ระบุ ต่างจากโหมดอื่นที่กดครบ 4 ตัว (`dismiss`, `done1`, `donee` ถูก merge เข้ามาใน templates แต่ loop ไม่ได้ใช้)

## Flow ต่อรอบ
1. เจอ `accept` กด
2. เจอ `draft-fight` กด
3. เจอ `draft-best` กดที่ (x กลางภาพ, y กลางภาพ + ครึ่งความสูงภาพ + 25)
4. เจอ `draft-victory` log `✓ พบ Draft-victory - เช็คปุ่ม Continue`
5. เจอ `continue` กด
6. พัก `loop_delay`

หลังคลิกแต่ละครั้งพัก 0.5 วินาที ตอนเริ่มถ้า key ใน `DRAFT_REQUIRED_KEYS` (`main.py:64`) ไม่ครบ หรือโหลดภาพ `draft-best` ไม่ได้ จะ log `✗` แล้วหยุด ความสูงของ `draft-best` อ่านครั้งเดียวก่อนเข้า loop ผ่าน `GameControl.template_size` (`lib/game_control.py:144`)

เหตุที่ไม่จำ step: โหมด [[Modes/Even|even]] เคยจำ step แล้วค้างเมื่อคลิกพลาด (แก้ใน 1.0.4) โหมด draft จึงเช็คทุกปุ่มทุกรอบตั้งแต่แรก

## ประวัติ
- 2026-09-13 เพิ่มโหมด draft (v1.0.5, ยังไม่ได้ทดสอบกับเกมจริง)

## Template notes
- 2026-09-13 `draft-best` (327×462) มีป้ายชื่อตัวละคร ("Rider") และฉากหลังเคลื่อนไหวติดอยู่ในภาพ ถ้าตัวละครหรือฉากเปลี่ยน score อาจไม่ถึง 0.6 ถ้าเจอปัญหาให้ crop เหลือแค่ตัวอักษร "Best of All" แต่จุดคลิกคำนวณจากขอบล่างของภาพ crop ใหม่แล้วจุดคลิกจะเลื่อนขึ้นตาม ต้องปรับ `DRAFT_BEST_CLICK_OFFSET` ด้วย
- 2026-09-13 `draft-victory` (355×178) มีตัวละครฉากหลังติดมา ความเสี่ยงแบบเดียวกัน