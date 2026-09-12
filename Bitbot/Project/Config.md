---
title: Config
type: reference
tags:
- mygamebot
- config
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/project/config
---

# config.json

ไฟล์นี้ถูกแพ็กเข้าไปใน exe ด้วย ถ้าเปลี่ยนชื่อ key ต้องระวังผู้ใช้ที่ยังใช้ build เก่า

| Key | ค่าปัจจุบัน | ความหมาย |
| --- | --- | --- |
| `window_title` | `陰陽師Onmyoji` | ชื่อหน้าต่างเกม ถ้าไม่เจอชื่อตรงจะลองหาชื่อที่มีคำนี้อยู่ |
| `confidence_threshold` | `0.6` | score ขั้นต่ำที่นับว่าเจอ template (ทุกโหมดยกเว้น realm) |
| `realm_confidence` | `0.85` | threshold เฉพาะโหมด realm |
| `loop_delay` | `1.0` | วินาทีที่พักระหว่างรอบสแกน |
| `update.enabled` | `true` | เปิด auto-update |
| `update.release_api_url` | GitHub API `Nontawaterr/MyGameBot/releases/latest` | แหล่ง release |
| `update.manifest_asset_name` | `release.json` | |
| `update.asset_name` | `Rubitdd-Bot-Release.zip` | |

## Template groups
| Section | โหมด | Keys |
| --- | --- | --- |
| `shared_templates` | ทุกโหมด | accept, dismiss, done1, donee |
| `templates` | [[Modes/Soul\|soul]] | start, continue, clear |
| `sougenbi_templates` | [[Modes/Sougenbi\|sougenbi]] | start, donee1 |
| `realm_templates` | [[Modes/Realm\|realm]] | hogan, next, attack, mark, lose, lose1 |
| `yonder_templates` | [[Modes/Yonder\|yonder]] | challenge (`.jpg`), continue, clear |
| `even_templates` | [[Modes/Even\|even]] | even-1, even-2, continue-1, continue-2 |
| `draft_templates` | [[Modes/Draft\|draft]] | draft-fight, draft-best, draft-victory, continue (ชี้ไป `assets/continue.png`) |

**กฎการรวม:** `{**shared, **mode}` ถ้า key ซ้ำ ค่าของโหมดจะชนะ ทำให้ override ภาพ shared เฉพาะโหมดได้
**ลำดับ key มีผล:** loop แบบ generic กดตามลำดับ dict คือ shared ก่อน แล้วตามด้วย key ของโหมด

## ตรวจสอบ
`project_check.py` เช็คว่า path ทุกตัวมีไฟล์อยู่จริง, มี section ครบตาม `MODE_TEMPLATE_KEYS` และทุกโฟลเดอร์ถูกใส่ใน build แล้ว