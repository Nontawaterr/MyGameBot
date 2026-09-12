---
title: Build and Release
type: reference
tags:
- mygamebot
- release
- build
created: 2026-09-11
updated: 2026-09-13
permalink: bitbot/project/build-and-release
---

# Build และ Release

## ขั้นตอน
1. bump `lib/version.py` (`APP_VERSION`) แล้ว commit แบบ `Bump version to X.Y.Z`
2. รัน `project_check.py`, `ruff check .`, `pytest`
3. `cmd /c "build.bat < nul"` จะได้ `dist\Rubitdd-Bot.exe` (onefile, noconsole, icon `app.ico`)
4. เปิด exe ดูว่าหน้าต่างขึ้นและชื่อเป็นเวอร์ชันใหม่
5. `cmd /c "make_release.bat < nul"` จะได้ `Rubitdd-Bot-Release.zip` และ `release.json`
6. เช็คว่า `release.json.sha256` ตรงกับ `Get-FileHash` ของ **zip** (ไม่ใช่ exe)
7. อัปโหลดทั้งสองไฟล์ขึ้น GitHub Release `vX.Y.Z`
8. เพิ่มรายการใน [[Changelog]]

> [!warning] `build.bat` และ `make_release.bat` จบด้วย `pause`
> ถ้าให้ agent หรือสคริปต์รัน ต้องต่อท้ายด้วย `< nul` ไม่อย่างนั้นจะค้าง
> ทั้งสองไฟล์ใช้ `python` และ `pyinstaller` จาก PATH ให้ activate `.venv` ก่อน

## ไฟล์ที่ bundle เข้า exe
`assets`, `sougenbi`, `realm`, `yonder`, `even`, `draft`, `config.json`
กำหนดไว้ **สองที่** คือ `build.bat` (`--add-data`) และ `Rubitdd-Bot.spec` (`datas`) ถ้าเพิ่มโฟลเดอร์ใหม่ต้องแก้ทั้งสองที่

## release.json
```json
{ "version": "1.0.3", "asset_name": "Rubitdd-Bot-Release.zip", "asset_url": "", "sha256": "<lowercase>", "notes": "" }
```

## Auto-update
(`lib/updater.py`)
- ทำงานเฉพาะตอนรันจาก exe (`sys.frozen`) และ `update.enabled`
- ดึง release ล่าสุดจาก GitHub API → หา asset `release.json` → เทียบเวอร์ชันด้วย `normalize_version`
- ถ้าเวอร์ชันใหม่กว่า จะถามผู้ใช้ → ดาวน์โหลด zip → เช็ค SHA-256 → แตกไฟล์ → รัน PowerShell helper ที่รอให้แอปปิด แล้วคัดลอกไฟล์ทับและเปิดแอปใหม่
- ถ้ายังไม่มี release (HTTP 404) จะเงียบไป ไม่ถือเป็น error
- ⚠️ ถ้า `sha256` ใน manifest ว่าง จะข้ามการตรวจ hash ดู [[Known Issues]]