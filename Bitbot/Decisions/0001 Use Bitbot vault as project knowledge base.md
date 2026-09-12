---
title: 0001 Use Bitbot vault as project knowledge base
type: decision
status: accepted
tags:
- decision
- tooling
created: 2026-09-11
permalink: bitbot/decisions/0001-use-bitbot-vault-as-project-knowledge-base
---

# 0001 ใช้ Obsidian vault `Bitbot/` เป็นคลังความรู้หลักของโปรเจค

ก่อนหน้านี้ความรู้ของโปรเจคกระจายอยู่หลายที่ ทั้ง `CLAUDE.md`, `AGENTS.md`, `.memory/` (basic-memory project `mygamebot`) และ skill ของ Codex
จึงตัดสินใจให้ `Bitbot/` เป็นที่บันทึกหลักสำหรับ session, โหมด, changelog, known issues และ decisions โดยเขียนเป็นภาษาไทย

- ใช้ basic-memory project `bitbot` ชี้มาที่ vault นี้ และเปิดให้ Claude ใช้ผ่าน MCP `bitbot-memory`
- `CONTEXT.md` ยังเป็นแหล่งอ้างอิงคำศัพท์หลัก ส่วน `CLAUDE.md` เก็บแค่คำสั่งและกฎที่ agent ต้องรู้ทุกครั้ง
- `.memory/` เก็บไว้เป็น legacy และไม่เขียนเพิ่ม