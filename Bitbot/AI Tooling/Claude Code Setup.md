---
title: Claude Code Setup
type: reference
tags:
- mygamebot
- ai
- claude-code
- tooling
created: 2026-09-11
updated: 2026-09-11
permalink: bitbot/ai-tooling/claude-code-setup
---

# Claude Code Setup

ติดตั้งเมื่อ 2026-09-11 ดู [[Sessions/2026-09-11 Claude Code tooling setup]]
(`.claude/` อยู่ใน `.gitignore` จึงไม่ถูก commit ถ้าลบโฟลเดอร์นี้ ต้องสร้างใหม่จากโน้ตนี้)

## Context files (root ของ repo)
| ไฟล์ | ใช้ทำอะไร |
| --- | --- |
| `CLAUDE.md` | คำสั่ง, สถาปัตยกรรม, กฎโค้ด, รายการ tooling, วิธีใช้ vault (Claude โหลดทุก session) |
| `AGENTS.md` | เวอร์ชันสำหรับ Codex และ agent อื่น |
| `CONTEXT.md` | คำศัพท์โดเมน แหล่งอ้างอิงหลัก (เพิ่ม Scan Loop, Step Sequence, Hogan Block, Shared Template) |

## Skills (`.claude/skills/`)
| Skill | ใช้เมื่อ |
| --- | --- |
| `rubitdd-bot-maintainer` | งานแก้โค้ดทั่วไป มีกฎสำคัญและ `scripts/project_check.py` |
| `add-bot-mode` | เพิ่มโหมดหรือแท็บใหม่ ทำครบตั้งแต่ภาพจนถึง build และเอกสาร |
| `template-tuning` | บอทไม่กดหรือกดผิด มี `scripts/match_debug.py` สำหรับวัด score, จับภาพ, crop |
| `bitbot-vault` | กฎการเขียนโน้ตใน vault นี้ |
| `grill-with-docs` | ซักถามออกแบบก่อนลงมือ อัปเดต `CONTEXT.md` และ [[Decisions/0001 Use Bitbot vault as project knowledge base\|ADR]] |
| `memory` | basic-memory CLI (ติดตั้งเดิม อัปเดตให้ใช้ project `bitbot`) |
| `context-window-management` | จัดการ context ยาว (ติดตั้งเดิม) |

## Subagents (`.claude/agents/`)
| Agent | หน้าที่ | สิทธิ์ |
| --- | --- | --- |
| `automation-reviewer` | รีวิว diff ของ `main.py`, `lib/`, `config.json`: thread, Win32, template, updater | อ่านอย่างเดียว + รัน check |
| `template-debugger` | หาสาเหตุที่ template ไม่ match ด้วย `match_debug.py` | ไม่เขียนทับภาพหรือ config |
| `release-manager` | เช็คเวอร์ชัน → check → build → zip → ตรวจ hash | ไม่ push หรืออัปโหลดถ้ายังไม่ได้อนุญาต |
| `bitbot-scribe` | เขียนหรืออัปเดตโน้ตใน `Bitbot/` | แก้ได้เฉพาะ `Bitbot/**/*.md` |

## MCP (`.mcp.json`)
| Server | คำสั่ง | ความสามารถ |
| --- | --- | --- |
| `bitbot-memory` | `basic-memory mcp --project bitbot` | ค้นหาแบบ semantic, `build_context`, `write_note` บน vault นี้ |

- ลงทะเบียน basic-memory project แล้วด้วย `basic-memory project add bitbot E:\1Web-Program\MyGameBot\Bitbot` (default project ยังเป็น `mygamebot`)
- basic-memory อาจเติม `permalink:` ใน frontmatter ของโน้ตเอง เป็นเรื่องปกติ

## Settings (`.claude/settings.json`)
- อนุญาตล่วงหน้า: `git status`/`diff`/`log`, pytest, ruff, `project_check.py`, `match_debug.py` ผ่าน `.venv`, และแก้ไฟล์ใน `Bitbot/**`
- `enabledMcpjsonServers: ["bitbot-memory"]`

## ตัวอย่างการสั่งงาน
- "โหมด realm ไม่กด attack ช่วยดูหน่อย" → `template-debugger`
- "เพิ่มโหมดใหม่ชื่อ xxx กด A แล้ว B" → skill `add-bot-mode`
- "รีวิวที่แก้ไปก่อน commit" → `automation-reviewer`
- "ออกเวอร์ชัน 1.0.4" → `release-manager`
- "บันทึกสิ่งที่ทำวันนี้ลง Obsidian" → `bitbot-scribe`

## ของเดิมที่ยังอยู่
- `.codex/skills/` (Codex): `rubitdd-bot-maintainer` เวอร์ชันเก่า และ `grill-with-docs`
- `.agents/skills/`: สำเนาของ `memory`, `context-window-management` จาก `skills-lock.json`
- `.memory/` (basic-memory `mygamebot`) เป็น legacy