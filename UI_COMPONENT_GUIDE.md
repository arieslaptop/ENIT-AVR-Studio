# ENIT AVR Studio — UI Component Guide
**Version**: 1.0.0  
**Project**: ENIT AVR Studio  
**Copyright**: &copy; 2026 Aries Computer Solutions, Harshad Patel, India  
**Design Reference**: Google Stitch MCP (`projects/12372459068504462501`)

---

## 1. Component Hierarchy & Layout

```
QMainWindow (EnitAVRStudio)
│
├── HeaderFrame
│   ├── Title & Subtitle ("ENIT AVR STUDIO")
│   ├── pill_hardware (Live Status LED + Hardware Summary Pill)
│   └── Copyright Attribution Banner ("Aries Computer Solutions")
│
├── toolbar_group (HARDWARE CONTROL & DEVICE WORKFLOW)
│   ├── btn_connect ("Connect USBasp")
│   ├── btn_autodetect ("Auto-Detect Chip")
│   ├── combo_chips (39 Microcontrollers Dropdown)
│   ├── combo_speed (ISP SCK Speed Selector)
│   ├── btn_read_all (Emerald "Read All")
│   ├── btn_write_all (Crimson "Write All")
│   ├── btn_erase (Red "Chip Erase")
│   └── btn_zif ("ZIF Socket Guide")
│
├── TelemetryHUD Frame
│   ├── lbl_telem_status (Action & Operation Status)
│   ├── lbl_telem_rate (Real-time Throughput B/s & KB/s)
│   ├── lbl_telem_time (Elapsed Time & Dynamic ETA)
│   └── lbl_telem_integrity (CRC32 Data Verification Indicator)
│
├── Main Tabbed Workspace (QTabWidget)
│   ├── Tab 1: Flash Memory (HEX)
│   │   ├── Action Bar (Load HEX, Save HEX, Read, Write, Verify, Clear)
│   │   ├── lbl_flash_info (Flash Statistics & Buffer Status)
│   │   └── tbl_flash (18-column Hex Matrix: Offset + 16 Bytes + Decoded ASCII)
│   │
│   ├── Tab 2: EEPROM Memory
│   │   ├── Action Bar (Load EEP, Save EEP, Read, Write, Verify, Clear)
│   │   ├── lbl_eeprom_info (EEPROM Statistics)
│   │   └── tbl_eeprom (18-column Hex Matrix)
│   │
│   ├── Tab 3: Fuse Bits / Settings
│   │   ├── 5 Dedicated Fuse Cards:
│   │   │   ├── Low Fuse Card (Write Checkbox, 0x Hex, Bit Details...)
│   │   │   ├── High Fuse Card (Write Checkbox, 0x Hex, Bit Details...)
│   │   │   ├── Extended Fuse Card (Write Checkbox, 0x Hex, Bit Details...)
│   │   │   ├── Lock Fuse Card (Write Checkbox, 0x Hex, Read/Write)
│   │   │   └── Calibration Card (Read-only Factory Calibrated Byte)
│   │   ├── Center Actions (Read Fuses, Write Selected Fuses)
│   │   └── Advanced Tools (Configure AVR Clock Wizard, Reset Defaults, ZIF Guide)
│   │
│   └── Tab 4: Telemetry & Hardware Log
│       ├── Action Bar (Clear Console, Test Connection, Export Log)
│       └── txt_log (High-resolution Timestamped Event Log)
│
└── Status Bar Frame
    ├── lbl_status (Bottom Global Status Message)
    └── progress_bar (Dual-tone Gradient Operation Progress)
```

---

## 2. Interactive Dialog Specifications

### 2.1 `EnitConfirmDialog`
- **Purpose**: High-contrast Cyber-Dark replacement for native Windows modal message boxes. Eliminates white-on-white bleached text.
- **Visuals**:
  - Machined dark slate background (`#171b26`), border `1px solid #334155`.
  - Amber/Cyan badge icon (`⚡`).
  - Itemized hardware sequence preview box (`#0b0f19`).
  - Action buttons: "Cancel" (Slate `#334155`) and "Yes, Proceed" (Danger Crimson `#dc2626` / Success Emerald `#059669`).

### 2.2 `ZIFPlacementDialog`
- **Purpose**: Displays physical DIP socket insertion diagrams for the selected microcontroller.
- **Assets**: Dynamically resolves `ZIF_DIP_28.bmp` and `ZIF_DIP_40.bmp`.
- **Instructions**: Illustrates Pin 1 notch orientation facing towards the ZIF socket lever handle, and warns to lock the lever down before programming.

### 2.3 `BitDetailsDialog`
- **Purpose**: Individual bitfield inspection and modification for Low, High, Ext, and Lock fuses.
- **Rules**: In AVR architecture, `0` = Programmed (Unchecked), `1` = Unprogrammed (Checked). Dynamic recalculation updates hex inputs in real-time.

### 2.4 `ClockConfigDialog`
- **Purpose**: Guided wizard for configuring internal RC oscillators, external crystals, and resonator clock options without risking microcontroller lock-out.

---

## 3. Application Icon Suite (`Icons/`)

The application features a complete set of optimized Windows `.ico` and transparent `.png` icons derived from the **Antigravity ENIT** levitating IC chip design, adhering to Windows Desktop UX guidelines:

| Size | Variant Style | Optimized For | Formats Available |
|:---:|:---|:---|:---:|
| **256&times;256** | Full 3D dynamic levitating IC chip with embossed "ENIT" and cyan antigravity energy field | Windows File Explorer Extra Large view, High-DPI screens | `.ico`, `.png` |
| **128&times;128** | Full 3D dynamic levitating IC chip with chrome pins and glowing aura | Windows File Explorer Large icons, Desktop 4K display | `.ico`, `.png` |
| **64&times;64** | Text-floating variant ("ENIT" typography hovering above glowing IC) | Windows Alt+Tab task switcher, Explorer Medium view | `.ico`, `.png` |
| **48&times;48** | Text-floating variant with high-contrast outlines | Standard Windows desktop shortcuts, Start Menu tiles | `.ico`, `.png` |
| **32&times;32** | Simplified clean glowing IC chip with razor-sharp legible "ENIT" | Windows Taskbar pinned icon, File Explorer Details view | `.ico`, `.png` |
| **16&times;16** | Ultra-crisp pixel-aligned micro IC chip with maximum glyph legibility | Window Titlebar, System Tray, File Explorer List view | `.ico`, `.png` |
| **Master** | Multi-Resolution Container (`enit_avr_studio.ico`) | Embedded directly into Windows application and process handle | `.ico` (All 6 sizes) |


