---
name: grill-with-docs
description: Run architecture and implementation grilling sessions for MyGameBot. Use when planning bot behavior changes, adding game modes/assets, changing updater/build flow, or clarifying project terms; keep CONTEXT.md and ADRs aligned with decisions.
---

<what-to-do>

Challenge the proposal with focused one-by-one questions until the decision is precise and testable. For each question, also provide your recommended answer and the trade-off.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, inspect code first and then ask only unresolved questions.

</what-to-do>

<supporting-info>

## Project-specific scope

Target this repository:

- UI and mode control: `main.py`
- Window automation and image matching: `lib/game_control.py`
- Update/version logic: `lib/updater.py`, `lib/version.py`
- Runtime config and templates: `config.json`, `assets/`, `sougenbi/`, `realm/`, `yonder/`
- Packaging: `build.bat`, `make_release.bat`, `Rubitdd-Bot.spec`

### Decision focus

- Template matching thresholds and loop timing
- Per-mode button sequences and click behavior
- Background-window constraints and failure handling
- Config schema changes and backward compatibility
- Build/release behavior and update mechanism

## Documentation behavior

Maintain root `CONTEXT.md` as glossary only. No implementation details.

Create `docs/adr/` lazily when a decision is hard to reverse, surprising, and trade-off based.

## During the session

### Challenge against glossary and code

When the user says "mode", confirm which tab (`soul`, `sougenbi`, `realm`, `yonder`) and required button sequence. If code and statements conflict, surface it immediately.

### Ask scenario-driven questions

Probe edge cases: minimized game window, missing template file, false-positive image match, and start/stop race between tabs.

### Update CONTEXT.md inline

When terms are clarified, update `CONTEXT.md` immediately using [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

### Offer ADRs sparingly

Use [ADR-FORMAT.md](./ADR-FORMAT.md) only for high-impact decisions such as update strategy, threading model changes, or major template-detection policy changes.

</supporting-info>
