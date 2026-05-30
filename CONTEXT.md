# MyGameBot Context

MyGameBot is a Windows desktop automation bot for Onmyoji. It detects UI templates from the game window and performs background clicks by mode.

## Language

**Mode**:
A self-contained automation flow mapped to one UI tab and one template group in `config.json`.
_Avoid_: profile, scene

**Template**:
An image file used for OpenCV matching to find a clickable UI element in the game window.
_Avoid_: icon, sprite

**Template Group**:
A named set of templates for one mode, such as `templates`, `sougenbi_templates`, `realm_templates`, or `yonder_templates`.
_Avoid_: preset, bundle

**Target Window**:
The game window selected by `window_title` and controlled through Win32 APIs.
_Avoid_: screen, monitor

**Background Click**:
A click sent to the target window without moving the physical mouse pointer.
_Avoid_: auto-click, simulated tap

**Confidence Threshold**:
The minimum match score required for a template to count as found.
_Avoid_: sensitivity, certainty

**Loop Delay**:
The wait interval between scan cycles in each running mode loop.
_Avoid_: frame rate, latency
