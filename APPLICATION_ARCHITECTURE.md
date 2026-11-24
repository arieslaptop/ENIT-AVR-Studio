# ENIT AVR Studio — Application Architecture
**Version**: 1.0.0  
**Project**: ENIT AVR Studio  
**Copyright**: &copy; 2026 Aries Computer Solutions, Harshad Patel, India  
**Target Hardware**: USBasp Programmer (`16c0:05dc`) & Atmel / Microchip AVR Family

---

## 1. System Overview

ENIT AVR Studio is an industrial clean-room microcontroller programming suite and hardware diagnostic platform built in Python 3.12 and PySide6 (Qt 6.7). It communicates directly with standard USBasp hardware via ctypes bindings to `libusb0.dll`, completely bypassing legacy 32-bit wrappers and providing native 64-bit performance on Windows 10/11.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          ENIT AVR Studio GUI                           │
│     (PySide6 / Qt 6.7 Dark Cyber Interface - Google Stitch Design)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Qt Signals / Slots
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Background Worker Thread                        │
│                (Non-Blocking QThread Hardware Pipeline)                │
└─────────┬─────────────────────────┬──────────────────────────┬─────────┘
          │                         │                          │
          ▼                         ▼                          ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  enit_chip_db    │      │ enit_hex_parser  │      │  enit_avr_core   │
│  (39 Chip XML DB │      │ (Intel HEX Parser│      │ (ctypes USBasp   │
│   & Fuse Layout) │      │  & Serializer)   │      │  ISP Driver)     │
└──────────────────┘      └──────────────────┘      └──────────┬───────┘
                                                               │
                                                               ▼
                                                    ┌──────────────────┐
                                                    │   libusb0.dll    │
                                                    │  (Direct Driver) │
                                                    └──────────┬───────┘
                                                               │
                                                               ▼
                                                    ┌──────────────────┐
                                                    │ USBasp Hardware  │
                                                    │  (16c0:05dc)     │
                                                    └──────────┬───────┘
                                                               │ SPI ISP
                                                               ▼
                                                    ┌──────────────────┐
                                                    │ Target AVR MCU   │
                                                    │ (e.g. ATmega328P)│
                                                    └──────────────────┘
```

---

## 2. Core Modules

### 2.1 `enit_avr_core.py` (Universal USBasp ISP Engine)
- **Direct USB Transfer Engine**: Implements the USBasp V-USB control endpoint protocol (`bmRequestType = 0xC0` for read, `0x40` for write).
- **Control Functions**:
  - `USBASP_FUNC_CONNECT` (`1`): Pulls target RESET low and clocks SCK pulses for sync.
  - `USBASP_FUNC_DISCONNECT` (`2`): Releases RESET line to run target application.
  - `USBASP_FUNC_TRANSMIT` (`3`): 4-byte raw SPI ISP transaction (`0xAC, 0x53, 0x00, 0x00`).
  - `USBASP_FUNC_READFLASH` (`4`): Fast block read with auto-incrementing address pointer.
  - `USBASP_FUNC_ENABLEEXTADDR` (`5`): Extended 128KB/256KB addressing for ATmega2560.
  - `USBASP_FUNC_WRITEFLASH` (`6`): Accelerated page write committing blocks with `wIndex = page_size | (3 << 8)`.
  - `USBASP_FUNC_READEEPROM` (`7`) & `USBASP_FUNC_WRITEEEPROM` (`8`): EEPROM read/write.
  - `USBASP_FUNC_SETSCKSPEED` (`9`): Dynamic ISP clock configuration (Auto, 375 kHz, 1.5 MHz, 32 kHz).

### 2.2 `enit_chip_db.py` (Universal 39-Chip Hardware Database)
- Parses `Data/chips.xml` and `Data/fuselayout.xml` dynamically.
- Automatically handles little-endian byte ordering in signatures (e.g., `0x000F951E` &rarr; `(0x1E, 0x95, 0x0F)`).
- Maps Low, High, Extended, and Lock bits to interactive named bitfields with descriptions and default states.

### 2.3 `enit_hex_parser.py` (Intel HEX & Memory Engine)
- Zero-dependency parser supporting Record Types `00` (Data), `01` (EOF), `02` (Extended Segment Address), and `04` (Extended Linear Address).
- Full bidrectional serialization to Intel HEX format with standard checksum validation.

### 2.4 `enit_avr_studio_gui.py` (Presentation & Telemetry Tier)
- High-performance PySide6 GUI built upon the Google Stitch Design System.
- Responsive scaling from 1280x720 up to 4K (3840x2160) with Windows High-DPI PassThrough policy.
- Real-time telemetry streaming at 60 FPS without blocking the user interface.

