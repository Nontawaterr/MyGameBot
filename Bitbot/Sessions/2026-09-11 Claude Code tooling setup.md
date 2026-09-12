---
title: 2026-09-11 Claude Code tooling setup
type: session
tags:
- session
- tooling
created: 2026-09-11
permalink: bitbot/sessions/2026-09-11-claude-code-tooling-setup
---

# 2026-09-11: ติดตั้ง Claude Code tooling และสร้าง vault

## เป้าหมาย
ติดตั้งและจัดระเบียบ skill, MCP, subagent และ context file ที่ช่วยทำงานในโปรเจคนี้ แล้วบันทึกความรู้ทั้งหมดลง Obsidian vault `Bitbot/`

## สิ่งที่ทำ
- สำรวจของเดิม ได้แก่ `CLAUDE.md`, `AGENTS.md`, `CONTEXT.md`, `.codex/skills`, `.claude/skills` (memory, context-window-management), `.memory/` และ vault ที่ยังว่าง
- สร้าง skills ใน `.claude/skills/`: `rubitdd-bot-maintainer` (ย้ายจาก Codex และแก้ `project_check.py` ให้เช็ค template path ทุกตัวและ bundle list), `add-bot-mode`, `template-tuning` (+ `match_debug.py`), `bitbot-vault`, `grill-with-docs` (ย้าย ADR มาไว้ใน vault)
- สร้าง subagents: `automation-reviewer`, `template-debugger`, `release-manager`, `bitbot-scribe`
- MCP: ลงทะเบียน basic-memory project `bitbot` และเพิ่ม `.mcp.json` server `bitbot-memory`
- `.claude/settings.json`: allowlist คำสั่ง check และเปิด MCP
- อัปเดต `CLAUDE.md` (Agent Tooling, Knowledge Base), `AGENTS.md` (โฟลเดอร์ even และ vault), `CONTEXT.md` (คำใหม่), `memory` skill (project `bitbot`)
- สร้างโน้ตใน vault: [[Home]], `Project/*`, `Modes/*`, [[Changelog]], [[Known Issues]], [[Decisions/0001 Use Bitbot vault as project knowledge base|ADR 0001]], [[AI Tooling/Claude Code Setup]], `Templates/*`
- ย้ายข้อมูลจาก `.memory/notes/MyGameBot Project Setup.md` มาไว้ใน Changelog และ Build and Release

## ผลการตรวจ
- `project_check.py` ✅ ผ่าน: 22 template paths, 5 โฟลเดอร์, bundle list ครบ, compile 5 ไฟล์
- `match_debug.py` self-test (offline) ✅ นำ `realm/attack.png` ไปวางบนภาพพื้นหลังสังเคราะห์ ได้ score 1.000 HIT ที่ตำแหน่งถูกต้อง template อื่นไม่ถึง 0.85 และ `--crop` ใช้งานได้
- ruff ของสคริปต์ใหม่ ✅ ผ่าน
- ruff ทั้ง repo ❌ มี 2 error ที่มีอยู่ก่อนแล้วใน `lib/game_control.py` (I001 import ไม่เรียง, F401 `sys` ไม่ได้ใช้) ยังไม่ได้แก้
- pytest ✅ 9 passed
- MCP `bitbot-memory` ✅ ทดสอบผ่าน stdio: initialize ได้, มี 23 tools, `search_notes "hogan"` เจอ [[Modes/Realm]] (score 1.19) และ sync เติม `permalink` ให้โน้ตแล้ว
- ⏳ ยังไม่ได้ทดสอบกับเกมจริง (`match_debug.py --mode ...` แบบ live)

## พบระหว่างทาง
- บัคและความเสี่ยง 10 ข้อ บันทึกไว้ที่ [[Known Issues]] ข้อสำคัญคือ GameControl ค้างหลังเปิดเกมใหม่ และ loop ซ้อนเมื่อกดหยุดแล้วเริ่มใหม่เร็ว ๆ

## ต่อไป
- [ ] เปิด session ใหม่ในโฟลเดอร์โปรเจคให้ Claude โหลด `.mcp.json` และ agents
- [ ] ทดลอง `match_debug.py --mode <mode>` ขณะเปิดเกม
- [ ] ตัดสินใจเรื่อง Known Issues #1–#3 (มี task แนะนำให้แก้ #1, #2 แล้ว)
- [ ] ตัดสินใจว่าจะ commit `Bitbot/` และ `.mcp.json` เข้า git หรือเพิ่มใน `.gitignore`