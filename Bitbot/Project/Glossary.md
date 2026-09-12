---
title: Glossary
type: reference
tags:
- mygamebot
- glossary
created: 2026-09-11
updated: 2026-09-11
permalink: bitbot/project/glossary
---

# คำศัพท์

แหล่งอ้างอิงหลักคือ `CONTEXT.md` ที่ root ของ repo ถ้ามีคำใหม่ให้แก้ที่นั่นก่อน โน้ตนี้เป็นแค่สรุปภาษาไทย

| คำ | ความหมาย | อย่าใช้ |
| --- | --- | --- |
| **Mode** | ชุด automation หนึ่งชุด ผูกกับแท็บหนึ่งแท็บ, template group หนึ่งกลุ่ม และ scan loop หนึ่งตัว | profile, scene |
| **Scan Loop** | รอบ "สแกนแล้วคลิก" ที่ทำซ้ำจนกดหยุด | farm loop |
| **Step Sequence** | ลำดับขั้นที่ต้องกดตามลำดับ แต่ละขั้นผ่านได้ด้วย template ใดก็ได้ในขั้นนั้น (โหมด even) | combo, macro |
| **Hogan Block** | สถานะในโหมด realm ที่หยุดกด `hogan` เพราะเห็น `mark` และจะปลดเมื่อกด `attack` | pause, lock |
| **Template** | ไฟล์ภาพที่ใช้หาปุ่มด้วย OpenCV | icon, sprite |
| **Template Group** | ชุด template ของโหมดหนึ่งใน `config.json` | preset |
| **Shared Template** | template ใน `shared_templates` ที่ถูกรวมเข้าทุกโหมด | global image |
| **Confidence Threshold** | score ขั้นต่ำที่นับว่าเจอ (realm ใช้ `realm_confidence`) | sensitivity |
| **Target Window** | หน้าต่างเกมที่เลือกด้วย `window_title` | screen |
| **Background Click** | คลิกผ่าน `PostMessage` โดยไม่ขยับเมาส์จริง | auto-click |
| **Loop Delay** | เวลาพักระหว่างรอบสแกน | frame rate |