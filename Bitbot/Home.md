---
title: Home
type: moc
tags:
- mygamebot
- index
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/home
---

# 🐇 Bitbot: คลังความรู้ Rubitdd-Bot

**Rubitdd-Bot** (repo `MyGameBot`) คือบอทอัตโนมัติสำหรับเกม **Onmyoji (陰陽師)** บน Windows
บอทจับภาพหน้าต่างเกม หาปุ่มด้วย OpenCV template matching แล้วคลิกแบบเบื้องหลัง จึงไม่ต้องขยับเมาส์จริง

- **เวอร์ชันล่าสุด:** `1.0.9` (2026-09-17)
- **โฟลเดอร์:** `E:\1Web-Program\MyGameBot`
- **GitHub:** `Nontawaterr/MyGameBot` (ใช้ Releases สำหรับ auto-update)

## 📘 โปรเจค
- [[Project/Overview|ภาพรวมและคำสั่ง]]
- [[Project/Architecture|สถาปัตยกรรม]]
- [[Project/Config|config.json]]
- [[Project/Build and Release|Build และ Release]]
- [[Project/Glossary|คำศัพท์]]

## 🎮 โหมด
| โหมด | รูปแบบ loop | Threshold | โฟลเดอร์ภาพ |
| --- | --- | --- | --- |
| [[Modes/Soul\|soul]] | กดทุกปุ่มที่เจอ (generic) | `confidence_threshold` | `assets/` |
| [[Modes/Sougenbi\|sougenbi]] | กดทุกปุ่มที่เจอ (generic) | `confidence_threshold` | `sougenbi/` |
| [[Modes/Realm\|realm]] | กฎเฉพาะ (hogan block) | `realm_confidence` | `realm/` |
| [[Modes/Yonder\|yonder]] | กดทุกปุ่มที่เจอ + ต้องมี `challenge` | `confidence_threshold` | `yonder/` |
| [[Modes/Even\|even]] | เลือกแท็บย่อย Farm / Activity แล้วกดทุกปุ่มที่เจอ (stateless) | `confidence_threshold` | `even/Farm/`, `even/activity/` |
| [[Modes/Draft\|draft]] | กฎเฉพาะแบบ stateless + offset click | `confidence_threshold` | `draft/` |
| [[Modes/Bondling\|bondling]] | ยังไม่มี loop (หน้า UI + ตัวเลือกย่อย ฟาม / จับ) | - | - |

ภาพที่ใช้ร่วมทุกโหมดอยู่ใน `assets/shared/`: accept, dismiss, done1, donee

## 🧭 ติดตามงาน
- [[Changelog]]
- [[Known Issues]]
- Decisions
  - [[Decisions/0001 Use Bitbot vault as project knowledge base]]
- Sessions
  - [[Sessions/2026-09-11 Claude Code tooling setup]]
  - [[Sessions/2026-09-13 เพิ่มโหมด draft]]
  - [[Sessions/2026-09-13 Bridge release แก้อัปเดต]]
  - [[Sessions/2026-09-13 แก้อัปเดตค้างและ temp รั่ว]]
  - [[Sessions/2026-09-13 เพิ่มแท็บ bondling]]

## 🤖 AI Tooling
- [[AI Tooling/Claude Code Setup]]