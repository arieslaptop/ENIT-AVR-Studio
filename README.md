# ENIT AVR Studio

> **Professional Microcontroller Programmer & Hardware Diagnostic Platform**  
> **Copyright &copy; 2026 Aries Computer Solutions &bull; Harshad Patel, India. All Rights Reserved.**

[![Platform: Windows x64](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://github.com/arieslaptop/ENIT-AVR-Studio)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![GUI: PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-orange.svg)](https://qt.io)
[![Hardware: USBasp ISP](https://img.shields.io/badge/Hardware-USBasp%20ISP-cyan.svg)](https://fischl.de/usbasp/)
[![Donate: PayPal](https://img.shields.io/badge/Sponsor-PayPal.Me-0079C1.svg)](https://paypal.me/ariestech)

---

## 🌟 Overview

**ENIT AVR Studio** is a modern, high-performance open-source Windows application designed for flashing, testing, and diagnosing Microchip/Atmel AVR 8-bit microcontrollers via **USBasp ISP programmers**. Built with an industrial cyber-dark aesthetic and Google Stitch design tokens, it offers superior reliability, non-blocking telemetry, intelligent page-skipping flash algorithms, comprehensive fuse configuration, and an interactive ZIF socket placement guide.

---

## ⚡ Key Features

- **🚀 Ultra-Fast Flashing Engine**:
  - Implements intelligent **0xFF blank page skipping**, eliminating redundant flash writes and boosting overall programming speed by up to 60–80%.
  - High-throughput USBasp bulk transfer pipe with automatic SCK frequency auto-tuning.
- **🛡️ 100% Bit-Exact Verification**:
  - Real-time post-write verification against Intel HEX buffers with byte-level discrepancy reporting and CRC32 telemetry integrity validation.
- **🔧 Advanced Fuse & Lock Bits Manager**:
  - Visual bit-by-bit manipulation of Low, High, Extended, and Lock fuse bytes.
  - Interactive **Fuse Details Dialog** with individual bit names (BODLEVEL, EESAVE, BOOTSZ, SPIEN, CKDIV8, etc.).
  - Built-in safety warnings to prevent accidental bricking or lockout.
  - One-click **Reset Fuses to Chip Defaults** feature.
- **⏱️ Interactive AVR Clock Generator**:
  - Clock frequency calculator with visual clock source selectors:
    - Internal Calibrated RC Oscillators (128 kHz, 1 MHz, 4 MHz, 8 MHz)
    - Low-Frequency Crystal Oscillators (32.768 kHz RTC)
    - Full-Swing and Low-Power External Ceramic/Quartz Crystals (up to 16+ MHz)
- **📚 Universal AVR Chip Database**:
  - Built-in comprehensive library covering 50+ AVR microcontrollers including:
    - **ATmega Series**: ATmega328P, ATmega328PB, ATmega16, ATmega32, ATmega8, ATmega8A, ATmega168P, ATmega88P, ATmega64, ATmega128, etc.
    - **ATtiny Series**: ATtiny85, ATtiny45, ATtiny13, ATtiny2313, ATtiny44, ATtiny84, etc.
    - **AT90S / Legacy Series**: AT90S8515, AT90S2313, etc.
- **🔌 ZIF Socket Placement Guide**:
  - Interactive visual pinout guidance showing exact IC insertion alignment in standard ZIF sockets for 28-pin DIP, 40-pin DIP, 20-pin DIP, and 8-pin DIP packages.
- **📊 Real-Time Telemetry HUD**:
  - Non-blocking multi-threaded architecture with dynamic status ribbon:
  - Throughput meter (B/s), Elapsed timer, ETA countdown, and live hardware log feed.
- **💻 Dual-Mode Architecture**:
  - **Full GUI Mode**: Standalone Windows application (`enit_avr_studio_gui.py` / `ENIT_AVR_Studio.exe`).
  - **Headless CLI Mode**: Command-line tool (`enit_avr_cli.py`) for automated factory flashing, testing rigs, and CI/CD pipelines.

---

## 📐 Hardware Connection & Schematic Guide

ENIT AVR Studio connects to target AVR microcontrollers via the standard **10-pin AVR ISP header** found on USBasp programmers.

### Circuit Schematic: USBasp to ATmega328P

![USBasp to ATmega328P Connection Schematic](Images/Schematics/usbasp_atmega328p_isp_schematic.png)

### Standard 10-Pin AVR ISP Header Pinout

```text
       AVR 10-Pin ISP Socket (Facing Male Pins / Female Plug)
                 +-----------+
    MOSI (Pin 1) | [1]   [2] | VCC (+5V)
      NC (Pin 3) | [3]   [4] | GND
   RESET (Pin 5) | [5]   [6] | GND
     SCK (Pin 7) | [7]   [8] | GND
    MISO (Pin 9) | [9]  [10] | GND
                 +-----------+
```

### Connection Table: USBasp to ATmega328P

| USBasp 10-Pin Header | Signal Name | Wire Color (Ref) | ATmega328P-AU (32-Pin TQFP) | ATmega328P (28-Pin DIP) | Function Description |
|:---:|:---:|:---:|:---:|:---:|:---|
| **Pin 1** | **MOSI** | Orange | Pin 15 (`PB3` / MOSI) | Pin 17 (`PB3` / MOSI) | Master Out Slave In |
| **Pin 2** | **VCC** | Red | Pin 4, 6 (`VCC`), Pin 18 (`AVCC`) | Pin 7 (`VCC`), Pin 20 (`AVCC`) | +5.0V Target Power Rail |
| **Pin 3** | **NC** | - | Not Connected | Not Connected | No Connection |
| **Pin 4, 6, 8, 10** | **GND** | Black | Pin 3, 5, 21 (`GND`) | Pin 8, 22 (`GND`) | Common Ground Return |
| **Pin 5** | **RESET** | Green | Pin 29 (`PC6` / RESET#) | Pin 1 (`PC6` / RESET#) | Active-Low ISP Reset line (10k pull-up to +5V) |
| **Pin 7** | **SCK** | Brown | Pin 17 (`PB5` / SCK) | Pin 19 (`PB5` / SCK) | Serial Programming Clock |
| **Pin 9** | **MISO** | Yellow | Pin 16 (`PB4` / MISO) | Pin 18 (`PB4` / MISO) | Master In Slave Out |

### Recommended External Components for Flashing Circuit
1. **Pull-up Resistor**: 10 kΩ resistor between `RESET` and `VCC` (+5V) to prevent spurious resets during operation.
2. **Decoupling Capacitors**: 10 µF electrolytic or ceramic capacitor across `VCC` and `GND`, and 10 µF on `AREF` to `GND`.
3. **Crystal Oscillator**: 16.000 MHz quartz crystal connected between `XTAL1` (Pin 7/PB6 on TQFP, Pin 9 on DIP) and `XTAL2` (Pin 8/PB7 on TQFP, Pin 10 on DIP), with two 22 pF ceramic load capacitors to GND.
4. **Status LED** (optional): Connected to Pin 14 (TQFP Pin 14 / DIP Pin 16) through a 470 Ω current-limiting resistor to GND.

---

## 💖 Support & Sponsorship (Open Source Community)

ENIT AVR Studio is maintained and actively developed as free, open-source software by **Aries Computer Solutions**, founded by **Harshad Patel in India**. 

Your sponsorships help acquire test hardware, fund new microcontroller protocol development, and keep these tools open and accessible to all developers:

- ☕ **[$10 USD Sponsorship](https://paypal.me/ariestech/10USD)**: Fund coffee, test cables, and server bandwidth.
- 🚀 **[$20 USD Sponsorship](https://paypal.me/ariestech/20USD)**: Sponsor new AVR microcontroller sample chips and test adapters.
- ✨ **[Custom Sponsorship Amount](https://paypal.me/ariestech)**: Any contribution via PayPal.Me is deeply appreciated!

**GitHub Repository**: [https://github.com/arieslaptop/ENIT-AVR-Studio](https://github.com/arieslaptop/ENIT-AVR-Studio)

---

## 🛠️ Quick Start & Installation

### Option 1: Standalone Windows Executable (No Python Required)
1. Download the latest `ENIT_AVR_Studio.exe` from the [Releases](https://github.com/arieslaptop/ENIT-AVR-Studio/releases) page.
2. Ensure your USBasp programmer has the `libusb-win32` driver installed (use [Zadig](https://zadig.akeo.ie/) if needed).
3. Double-click `ENIT_AVR_Studio.exe` to launch immediately.

### Option 2: Running from Source (Python 3.10+)
```powershell
# 1. Clone repository
git clone https://github.com/arieslaptop/ENIT-AVR-Studio.git
cd ENIT-AVR-Studio

# 2. Install dependencies
pip install PySide6 pyusb

# 3. Launch application
python enit_avr_studio_gui.py
```

Or double-click `run_enit_avr_studio.bat`.

---

## 💻 CLI Tool Usage (`enit_avr_cli.py`)

For automated workflows, test rigs, and terminal automation:

```powershell
# Auto-detect target chip and verify connection
python enit_avr_cli.py --detect

# Read Fuse and Lock bits
python enit_avr_cli.py -c ATmega328P --read-fuses

# Flash firmware HEX file with verification
python enit_avr_cli.py -c ATmega328P -wf myFirmware.hex -vf myFirmware.hex

# Complete Write-All (Erase, Flash, EEPROM, and Fuses in one go)
python enit_avr_cli.py -c ATmega328P -wf myFirmware.hex -we myEEPROM.eep -wF FF:DE:FD:FF --write-all
```

---

## 📁 Repository Structure

```text
ENIT-AVR-Studio/
├── .github/
│   └── FUNDING.yml             # GitHub Sponsors / PayPal.Me sponsorship config
├── Data/                       # Complete AVR chip database & fuse layouts XML
│   ├── chips.xml
│   └── fuselayout.xml
├── Icons/                      # Complete Windows .ico and .png icon suite (16x16 to 256x256)
│   └── enit_avr_studio.ico
├── Images/                     # UI visual assets, branding, and diagrams
│   ├── enit_logo.png           # Master clean ENIT 3D chip logo
│   ├── enit_logo_header.png    # Header rounded HUD logo
│   ├── Placements/             # ZIF socket placement diagrams
│   └── Schematics/             # Hardware connection schematics
│       └── usbasp_atmega328p_isp_schematic.png
├── enit_avr_studio_gui.py      # Main PySide6 GUI Application
├── enit_avr_core.py            # High-speed USBasp driver & ISP programming engine
├── enit_chip_db.py             # Chip signatures, memory configurations & fuse models
├── enit_hex_parser.py          # Fast Intel HEX & Motorola S-record parser
├── enit_avr_cli.py             # Production CLI automation tool
├── run_enit_avr_studio.bat     # Windows one-click launcher
├── DESIGN.md                   # Google Stitch Design System documentation
├── APPLICATION_ARCHITECTURE.md # System architecture specification
├── SECURITY_CHECKLIST.md       # Windows security & code signing guidelines
├── TESTING_REPORT.md           # Hardware flash verification logs (ATmega328P 100% pass)
└── README.md                   # Project overview & hardware schematic guide
```

---

## 📜 Copyright & License

Copyright &copy; 2026 **Aries Computer Solutions**  
Author: **Harshad Patel, India**  
All Rights Reserved.

Open source software distributed under the MIT License. Contributions and pull requests are warmly welcomed!

