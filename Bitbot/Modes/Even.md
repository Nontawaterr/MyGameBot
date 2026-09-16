---
title: Even
type: mode
tags:
- mygamebot
- mode
- even
created: 2026-09-11
updated: 2026-09-17
permalink: bitbot/modes/even
---

# โหมด even

- **แท็บ:** `even` (มีแท็บย่อยให้เลือกเหนือบรรทัดสถานะ)
- **Loop:** `_run_even(sub_key)` (`main.py`)
- **Config section:** `even_templates`
- **Threshold:** `confidence_threshold` (0.6)
- **รูปแบบ:** เลือก Sub-mode แล้วกดทุกปุ่มที่เจอในรอบนั้น (stateless ไม่จำว่ารอบก่อนกดอะไร)

## Sub-mode
| Key | ปุ่มบนแท็บ | Templates ที่กด |
| --- | --- | --- |
| `farm` | Farm | `farm-1` |
| `activity` | Activity | `activity-1`, `roll`, `activity-2`, `activity-3` |

ปุ่มเลือกอยู่เหนือบรรทัดสถานะ (`CTkSegmentedButton`) ค่าที่เลือกถูกอ่านบน Tk thread ตอนกด ▶ ผ่าน `_selected_sub_mode` แล้วส่งเข้า worker thread ถ้าจะเปลี่ยน sub-mode ต้องกดหยุดแล้วเริ่มใหม่

## Templates
| Key | ไฟล์ | บทบาท |
| --- | --- | --- |
| shared | `assets/shared/*` | accept, dismiss, done1, donee กดทุกตัวที่เจอทุกรอบ |
| `farm-1` | `even/Farm/farm-1.png` | ปุ่ม Challenge ของ Farm |
| `activity-1` | `even/activity/activity-1.png` | ปุ่ม Go (ลูกเต๋า) |
| `roll` | `even/activity/roll.png` | ปุ่ม Roll ยืนยันการทอยหลังกด Go |
| `activity-2` | `even/activity/activity-2.png` | ปุ่ม Challenge |
| `activity-3` | `even/activity/activity-3.png` | วงกลมบนกระดาน กดตรงกลางภาพ |
| `continue-1` | `assets/continue-1.png` | Tap to continue (ตัวหรี่) |
| `continue-2` | `assets/continue-2.png` | Tap to continue (ตัวสว่าง) |

## Flow ต่อรอบ
1. `_click_shared` กด accept, dismiss, done1, donee ที่เห็นทุกตัว
2. ไล่ template ของ sub-mode ที่เลือกตามลำดับ เจอตัวไหนกดตัวนั้น (Activity: Go → Roll → วงกลมบนกระดาน → Challenge)
3. `continue-1` หรือ `continue-2` เจออันไหนก่อนกดอันนั้นแล้วข้ามอีกอัน
4. พัก `loop_delay`

หลังคลิกแต่ละครั้งพัก 0.5 วินาที ตอนเริ่มถ้า key ของ sub-mode หรือ continue ไม่ครบใน config จะ log `✗` แล้วหยุด

## ประวัติ
- 2026-09-09 เพิ่มโหมด even
- 2026-09-10 เพิ่มปุ่ม continue (v1.0.2)
- 2026-09-10 ปรับให้กดตามลำดับ (v1.0.3)
- 2026-09-11 เลิกจำ step เช็คตามลำดับใหม่ทุกรอบ แก้ค้างเมื่อคลิกพลาด (v1.0.4)
- 2026-09-17 แยกเป็น sub-mode Farm / Activity ใช้ภาพชุดใหม่ใน `even/Farm/` และ `even/activity/` ส่วน `continue-1/2` ย้ายไป `assets/` และเลิกใช้ `EVEN_STEPS` (ยังไม่ได้ทดสอบกับเกมจริง)
- 2026-09-17 Activity เพิ่มเช็คปุ่ม `roll` แทรกหลัง `activity-1` (v1.0.9, ยังไม่ได้ทดสอบกับเกมจริง)

## Template notes
- 2026-09-17 `farm-1` กับ `activity-2` เป็นปุ่ม Challenge รูปเดียวกัน (145×118) ต่างกันแค่ชื่อไฟล์ตาม sub-mode
- 2026-09-17 `activity-3` ผู้ใช้ crop ใหม่ให้เหลือแค่วงกลม ไม่มีตัวเลขคะแนนติดมา จึงกดตรงกลางภาพได้เลย ไม่ต้องอ่านเลข
