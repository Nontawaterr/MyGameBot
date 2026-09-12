---
title: Realm
type: mode
tags:
- mygamebot
- mode
- realm
created: 2026-09-11
updated: 2026-09-11
permalink: bitbot/modes/realm
---

# โหมด realm (ตีเขต)

- **แท็บ:** `realm`
- **Loop:** `_run_realm` (`main.py:286`)
- **Config section:** `realm_templates`
- **Threshold:** `realm_confidence` (0.85) เข้มกว่าโหมดอื่นเพื่อกันกดผิด

## Templates
| Key | ไฟล์ | บทบาท |
| --- | --- | --- |
| done1 | `assets/shared/done1.png` | shared ปิดหน้าจบ |
| mark | `realm/mark.png` | ถ้าเห็นจะเปิด **Hogan Block** |
| hogan | `realm/hogan.png` | เป้าหมาย คลิกที่ **y + 40px** ใต้ภาพ |
| next | `realm/next.png` | |
| attack | `realm/attack.png` | กดแล้ว **ปลด Hogan Block** |
| lose | `realm/lose.png` | หน้าแพ้ พัก 1.5 วินาทีหลังกด |
| lose1 | `realm/lose1.png` | |

## Flow ต่อรอบ (ลำดับตายตัว)
1. `done1` → คลิก
2. `mark` → ถ้าเห็น ให้ `hogan_blocked = True`
3. `hogan` → ถ้ายังไม่ถูก block ให้คลิกที่ `(x, y+40)`
4. `next` → คลิก
5. `attack` → คลิก และถ้ากำลัง block อยู่ให้ปลด
6. `lose` → คลิก แล้วพัก 1.5 วินาที
7. `lose1` → คลิก
8. พัก `loop_delay`

> [!note] shared `accept`, `dismiss`, `donee` ถูกรวมเข้ามาใน templates ด้วย แต่ `_run_realm` ไม่ได้ใช้ ดู [[Known Issues]]

## ประวัติ
- 2026-05-31 ปรับตีเขต
- 2026-06-01 แก้บัคตีเขตไม่ได้ (v1.0.1)

## Template notes
- (ยังไม่มีบันทึก)