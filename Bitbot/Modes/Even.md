---
title: Even
type: mode
tags:
- mygamebot
- mode
- even
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/modes/even
---

# โหมด even

- **แท็บ:** `even` (แท็บสุดท้าย)
- **Loop:** `_run_even` (`main.py:411`)
- **Config section:** `even_templates`
- **Threshold:** `confidence_threshold` (0.6)
- **รูปแบบ:** Step Sequence ตาม `EVEN_STEPS` (`main.py:57`) เช็คใหม่จาก step 1 ทุกรอบ (stateless)

## Step Sequence
| Step | Templates (กดตัวไหนก็ได้) |
| --- | --- |
| 1 | `even-1` (`even/even-1.png`) |
| 2 | `even-2` (`even/even-2.png`) |
| 3 | `continue-1` หรือ `continue-2` (`even/continue-1.png`, `even/continue-2.png`) |
| → | กลับไป step 1 |

## Flow ต่อรอบ
1. `_click_shared` กด accept, dismiss, done1, donee ที่เห็นทุกตัว เพราะ popup โผล่ได้ทุกขั้น
2. ไล่เช็ค `EVEN_STEPS` จาก step 1 ทุกรอบ เจอ template แรกให้คลิกแล้วพัก 0.5 วินาที ไม่จำว่ารอบก่อนอยู่ step ไหน ถ้าคลิกพลาด รอบถัดไปจะเจอปุ่มเดิมและกดซ้ำ
3. พัก `loop_delay`

ตอนเริ่ม ถ้า key ใน `EVEN_STEPS` ไม่ครบจะ log `✗ ไม่พบ even_templates: ...` แล้วหยุด

## ประวัติ
- 2026-09-09 เพิ่มโหมด even
- 2026-09-10 เพิ่มปุ่ม continue (v1.0.2)
- 2026-09-10 ปรับให้กดตามลำดับ (v1.0.3)
- 2026-09-11 เลิกจำ step เช็คตามลำดับใหม่ทุกรอบ แก้ค้างเมื่อคลิกพลาด (v1.0.4)

## Template notes
- (ยังไม่มีบันทึก)