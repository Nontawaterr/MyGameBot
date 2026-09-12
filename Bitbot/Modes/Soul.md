---
title: Soul
type: mode
tags:
- mygamebot
- mode
- soul
created: 2026-09-11
updated: 2026-09-11
permalink: bitbot/modes/soul
---

# โหมด soul

- **แท็บ:** `soul` (แท็บแรก)
- **Loop:** `_run_generic` (`main.py:264`)
- **Config section:** `templates`
- **Threshold:** `confidence_threshold` (0.6)

## Templates (ลำดับการเช็คในแต่ละรอบ)
| Key | ไฟล์ | ที่มา |
| --- | --- | --- |
| accept | `assets/shared/accept.png` | shared |
| dismiss | `assets/shared/dismiss.png` | shared |
| done1 | `assets/shared/done1.png` | shared |
| donee | `assets/shared/donee.png` | shared |
| start | `assets/start.png` | soul |
| continue | `assets/continue.png` | soul |
| clear | `assets/clear.png` | soul |

## Flow
ในแต่ละรอบจะไล่เช็คทุก key ตามลำดับในตาราง ถ้าเจอก็คลิกกลางปุ่มแล้วพัก 0.5 วินาที
ครบทุก key แล้วพัก `loop_delay` ก่อนเริ่มรอบใหม่ ในรอบเดียวกันอาจคลิกได้หลายปุ่ม

## Template notes
- (ยังไม่มีบันทึก)