"""
================================================================================
ENIT AVR STUDIO - Microcontroller Hardware Database
Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India
All Rights Reserved.
================================================================================
"""

import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

@dataclass
class FuseBit:
    position: int
    name: str
    details: str
    default: int = 1

@dataclass
class FuseLayout:
    low_bits: List[FuseBit] = field(default_factory=list)
    high_bits: List[FuseBit] = field(default_factory=list)
    ext_bits: List[FuseBit] = field(default_factory=list)
    lock_bits: List[FuseBit] = field(default_factory=list)

@dataclass
class AVRChip:
    name: str
    flash_size: int         # bytes
    eeprom_size: int        # bytes
    page_size: int          # bytes
    signature: Tuple[int, int, int] # e.g. (0x1E, 0x95, 0x0F)
    has_lfuse: bool = True
    has_hfuse: bool = True
    has_efuse: bool = True
    has_lock: bool = True
    has_calib: bool = True
    default_lfuse: int = 0xFF
    default_hfuse: int = 0xDE
    default_efuse: int = 0xFD
    default_lock: int = 0xFF
    placement_image: str = ""
    fuse_layout: Optional[FuseLayout] = None

def parse_signature_int(sig_str: str) -> Tuple[int, int, int]:
    """Converts 0x000F951E hex string to (0x1E, 0x95, 0x0F) tuple."""
    try:
        val = int(sig_str, 16)
        b0 = val & 0xFF
        b1 = (val >> 8) & 0xFF
        b2 = (val >> 16) & 0xFF
        return (b0, b1, b2)
    except Exception:
        return (0, 0, 0)

# Global in-memory chip database
CHIP_DATABASE: Dict[str, AVRChip] = {}

def load_fuse_layouts_xml(xml_path: str) -> Dict[str, Dict[str, List[FuseBit]]]:
    """Loads all layouts from fuselayout.xml."""
    layouts = {"LOWFUSE": {}, "HIGHFUSE": {}, "EXTFUSE": {}}
    if not os.path.exists(xml_path):
        return layouts

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for tag in ["LOWFUSE", "HIGHFUSE", "EXTFUSE"]:
            section = root.find(tag)
            if section is not None:
                for layout_el in section.findall("LAYOUT"):
                    lid = layout_el.attrib.get("id", "1")
                    bits = []
                    for b_el in layout_el.findall("BIT"):
                        pos = int(b_el.attrib.get("position", "0"))
                        name = b_el.attrib.get("name", f"BIT{pos}")
                        details = b_el.attrib.get("details", "")
                        default_val = int(b_el.attrib.get("default", "1"))
                        bits.append(FuseBit(pos, name, details, default_val))
                    layouts[tag][lid] = sorted(bits, key=lambda x: x.position)
    except Exception as ex:
        print(f"Error parsing fuselayout.xml: {ex}")
    return layouts

# Standard lock bits layout
DEFAULT_LOCK_BITS = [
    FuseBit(0, "LB1", "Memory Lock Bit 1", 1),
    FuseBit(1, "LB2", "Memory Lock Bit 2", 1),
    FuseBit(2, "BLB01", "Boot Lock Bit 01", 1),
    FuseBit(3, "BLB02", "Boot Lock Bit 02", 1),
    FuseBit(4, "BLB11", "Boot Lock Bit 11", 1),
    FuseBit(5, "BLB12", "Boot Lock Bit 12", 1),
]

def _build_layout(low: List[FuseBit], high: List[FuseBit], ext: Optional[List[FuseBit]] = None) -> FuseLayout:
    return FuseLayout(
        low_bits=low,
        high_bits=high,
        ext_bits=ext if ext is not None else [],
        lock_bits=DEFAULT_LOCK_BITS
    )

def load_chips_xml(xml_path: str, layouts_path: str) -> Dict[str, AVRChip]:
    """Parses chips.xml and builds AVRChip catalog with attached fuse layouts."""
    chips: Dict[str, AVRChip] = {}
    layouts = load_fuse_layouts_xml(layouts_path)

    if not os.path.exists(xml_path):
        return chips

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for chip_el in root.findall("CHIP"):
            name = chip_el.findtext("NAME", "").strip()
            if not name:
                continue

            flash = int(chip_el.findtext("FLASH", "32768"))
            eeprom = int(chip_el.findtext("EEPROM", "1024"))
            page = int(chip_el.findtext("PAGE", "128"))
            sig_str = chip_el.findtext("SIG", "0x00000000")
            sig = parse_signature_int(sig_str)

            lf_el = chip_el.find("LFUSE")
            hf_el = chip_el.find("HFUSE")
            ef_el = chip_el.find("EFUSE")
            lock_text = chip_el.findtext("LOCK", "NO").strip().upper()
            calib_text = chip_el.findtext("CALIB", "NO").strip().upper()
            placement = chip_el.findtext("PLACEMENT", "")

            has_lf = lf_el is not None and lf_el.text == "YES"
            has_hf = hf_el is not None and hf_el.text == "YES"
            has_ef = ef_el is not None and ef_el.text == "YES"
            has_lock = lock_text == "YES"
            has_cal = calib_text == "YES"

            lf_layout_id = lf_el.attrib.get("layout", "1") if lf_el is not None else "1"
            hf_layout_id = hf_el.attrib.get("layout", "1") if hf_el is not None else "1"
            ef_layout_id = ef_el.attrib.get("layout", "1") if ef_el is not None else "1"

            # Resolve bitfields
            low_bits = layouts.get("LOWFUSE", {}).get(lf_layout_id, [])
            high_bits = layouts.get("HIGHFUSE", {}).get(hf_layout_id, [])
            ext_bits = layouts.get("EXTFUSE", {}).get(ef_layout_id, []) if has_ef else []

            # If layout XML didn't have bits, build standard AVR defaults
            if not low_bits:
                low_bits = [
                    FuseBit(0, "CKSEL0", "Clock select bit 0"),
                    FuseBit(1, "CKSEL1", "Clock select bit 1"),
                    FuseBit(2, "CKSEL2", "Clock select bit 2"),
                    FuseBit(3, "CKSEL3", "Clock select bit 3"),
                    FuseBit(4, "SUT0", "Start-up time bit 0"),
                    FuseBit(5, "SUT1", "Start-up time bit 1"),
                    FuseBit(6, "CKOUT", "Clock output"),
                    FuseBit(7, "CKDIV8", "Divide clock by 8"),
                ]
            if not high_bits:
                high_bits = [
                    FuseBit(0, "BOOTRST", "Select Reset Vector"),
                    FuseBit(1, "BOOTSZ0", "Boot size bit 0"),
                    FuseBit(2, "BOOTSZ1", "Boot size bit 1"),
                    FuseBit(3, "EESAVE", "Preserve EEPROM on Chip Erase"),
                    FuseBit(4, "WDTON", "Watchdog Timer Always On"),
                    FuseBit(5, "SPIEN", "Enable Serial (SPI) Programming"),
                    FuseBit(6, "DWEN", "debugWIRE Enable"),
                    FuseBit(7, "RSTDISBL", "External Reset Disable"),
                ]

            fuse_layout = FuseLayout(
                low_bits=low_bits,
                high_bits=high_bits,
                ext_bits=ext_bits,
                lock_bits=DEFAULT_LOCK_BITS
            )

            # Compute default fuse values from bits
            def_lf = 0
            for b in low_bits:
                if b.default: def_lf |= (1 << b.position)
            def_hf = 0
            for b in high_bits:
                if b.default: def_hf |= (1 << b.position)
            def_ef = 0
            for b in ext_bits:
                if b.default: def_ef |= (1 << b.position)

            if def_lf == 0: def_lf = 0xFF
            if def_hf == 0: def_hf = 0xDE
            if def_ef == 0: def_ef = 0xFD if has_ef else 0xFF

            # Page size in bytes: In chips.xml, ATmega328P says 64 (words), which is 128 bytes
            page_bytes = page
            if "328" in name or "168" in name or "16" in name or "32" in name:
                if page == 64:
                    page_bytes = 128
            elif "2560" in name or "1280" in name or "128" in name or "64" in name:
                if page < 256 and flash >= 65536:
                    page_bytes = 256

            chip_obj = AVRChip(
                name=name,
                flash_size=flash,
                eeprom_size=eeprom,
                page_size=page_bytes,
                signature=sig,
                has_lfuse=has_lf,
                has_hfuse=has_hf,
                has_efuse=has_ef,
                has_lock=has_lock,
                has_calib=has_cal,
                default_lfuse=def_lf,
                default_hfuse=def_hf,
                default_efuse=def_ef,
                default_lock=0xFF,
                placement_image=placement,
                fuse_layout=fuse_layout
            )
            chips[name] = chip_obj

    except Exception as ex:
        print(f"Error parsing chips.xml: {ex}")

    return chips

def init_chip_database():
    """Initializes the database by searching local and installed Data directories and adding modern variants."""
    global CHIP_DATABASE
    search_dirs = [
        os.path.join(BASE_DIR, "Data"),
        os.path.join(os.path.dirname(__file__), "Data"),
        r"C:\Program Files\eXtreme Burner - AVR\Data",
        r"D:\REA ATMEGA PROGRAM\ENIT_AVR_STUDIO\Data"
    ]

    loaded = False
    layouts = {}
    for d in search_dirs:
        chips_xml = os.path.join(d, "chips.xml")
        fuselayout_xml = os.path.join(d, "fuselayout.xml")
        if os.path.exists(chips_xml) and os.path.exists(fuselayout_xml):
            layouts = load_fuse_layouts_xml(fuselayout_xml)
            chips = load_chips_xml(chips_xml, fuselayout_xml)
            if chips:
                CHIP_DATABASE = chips
                loaded = True
                break

    # Reusable standard fuse bit definitions for expanded chips
    std_low_layout2 = layouts.get("LOWFUSE", {}).get("2", [
        FuseBit(0, "CKSEL0", "Clock select bit 0", 0),
        FuseBit(1, "CKSEL1", "Clock select bit 1", 1),
        FuseBit(2, "CKSEL2", "Clock select bit 2", 0),
        FuseBit(3, "CKSEL3", "Clock select bit 3", 0),
        FuseBit(4, "SUT0", "Start-up time bit 0", 0),
        FuseBit(5, "SUT1", "Start-up time bit 1", 1),
        FuseBit(6, "CKOUT", "Clock output", 1),
        FuseBit(7, "CKDIV8", "Divide clock by 8", 0),
    ])

    std_high_layout5 = layouts.get("HIGHFUSE", {}).get("5", [
        FuseBit(0, "BOOTRST", "Select Reset Vector", 1),
        FuseBit(1, "BOOTSZ0", "Select Boot Size", 0),
        FuseBit(2, "BOOTSZ1", "Select Boot Size", 0),
        FuseBit(3, "EESAVE", "Preserve EEPROM on Chip Erase", 1),
        FuseBit(4, "WDTON", "Watchdog Timer Always On", 1),
        FuseBit(5, "SPIEN", "Enable Serial (SPI) Programming", 0),
        FuseBit(6, "DWEN", "debugWIRE Enable", 1),
        FuseBit(7, "RSTDISBL", "External Reset Disable", 1),
    ])

    std_ext_layout4 = layouts.get("EXTFUSE", {}).get("4", [
        FuseBit(0, "BODLEVEL0", "Brown-out Detector trigger level", 1),
        FuseBit(1, "BODLEVEL1", "Brown-out Detector trigger level", 1),
        FuseBit(2, "BODLEVEL2", "Brown-out Detector trigger level", 1),
        FuseBit(3, "UNIMPLEMENTED", "---", 1),
        FuseBit(4, "UNIMPLEMENTED", "---", 1),
        FuseBit(5, "UNIMPLEMENTED", "---", 1),
        FuseBit(6, "UNIMPLEMENTED", "---", 1),
        FuseBit(7, "UNIMPLEMENTED", "---", 1),
    ])

    std_mega_old_low = layouts.get("LOWFUSE", {}).get("1", [
        FuseBit(0, "CKSEL0", "Select Clock source", 1),
        FuseBit(1, "CKSEL1", "Select Clock source", 0),
        FuseBit(2, "CKSEL2", "Select Clock source", 0),
        FuseBit(3, "CKSEL3", "Select Clock source", 0),
        FuseBit(4, "SUT0", "Select start-up time", 0),
        FuseBit(5, "SUT1", "Select start-up time", 1),
        FuseBit(6, "BODEN", "Brown out detector enable", 1),
        FuseBit(7, "BODLEVEL", "Brown out detector trigger level", 1),
    ])

    std_mega_old_high_m8 = layouts.get("HIGHFUSE", {}).get("1", [
        FuseBit(0, "BOOTRST", "Select Reset Vector", 1),
        FuseBit(1, "BOOTSZ0", "Select Boot Size", 0),
        FuseBit(2, "BOOTSZ1", "Select Boot Size", 0),
        FuseBit(3, "EESAVE", "EEPROM memory preserved through Chip Erase", 1),
        FuseBit(4, "CKOPT", "Oscillator options", 1),
        FuseBit(5, "SPIEN", "Enable Serial Program and Data Downloading", 0),
        FuseBit(6, "WDTON", "WDT always on", 1),
        FuseBit(7, "RSTDISBL", "Select if PC6 is I/O pin or RESET pin", 1),
    ])

    std_mega_old_high_m16_32 = layouts.get("HIGHFUSE", {}).get("2", [
        FuseBit(0, "BOOTRST", "Select Reset Vector", 1),
        FuseBit(1, "BOOTSZ0", "Select Boot Size", 0),
        FuseBit(2, "BOOTSZ1", "Select Boot Size", 0),
        FuseBit(3, "EESAVE", "EEPROM memory preserved through Chip Erase", 1),
        FuseBit(4, "CKOPT", "Oscillator options", 1),
        FuseBit(5, "SPIEN", "Enable Serial Program and Data Downloading", 0),
        FuseBit(6, "JTAGEN", "Enable JTAG", 0),
        FuseBit(7, "OCDEN", "Enable OCD", 1),
    ])

    tiny_8pin_low = [
        FuseBit(0, "CKSEL0", "Select Clock Source", 0),
        FuseBit(1, "CKSEL1", "Select Clock Source", 1),
        FuseBit(2, "SUT0", "Select start-up time", 0),
        FuseBit(3, "SUT1", "Select start-up time", 1),
        FuseBit(4, "CKOUT", "Clock Output enable", 1),
        FuseBit(5, "WDTON", "Watchdog Timer Always On", 1),
        FuseBit(6, "EESAVE", "Preserve EEPROM on Chip Erase", 1),
        FuseBit(7, "CKDIV8", "Divide clock by 8", 0),
    ]

    tiny_8pin_high = [
        FuseBit(0, "BODLEVEL0", "Brown-out Detector trigger level", 1),
        FuseBit(1, "BODLEVEL1", "Brown-out Detector trigger level", 1),
        FuseBit(2, "BODLEVEL2", "Brown-out Detector trigger level", 1),
        FuseBit(3, "DWEN", "debugWIRE Enable", 1),
        FuseBit(4, "SPMEN", "Self-programming Enable", 1),
        FuseBit(5, "RSTDISBL", "External Reset Disable", 1),
        FuseBit(6, "SPIEN", "Enable Serial (SPI) Programming", 0),
        FuseBit(7, "UNIMPLEMENTED", "---", 1),
    ]

    tiny_8pin_ext = [
        FuseBit(0, "SELFPRGEN", "Self Programming Enable", 1),
    ]

    usb32u4_high = [
        FuseBit(0, "BOOTRST", "Select Reset Vector", 0),
        FuseBit(1, "BOOTSZ0", "Select Boot Size", 0),
        FuseBit(2, "BOOTSZ1", "Select Boot Size", 0),
        FuseBit(3, "EESAVE", "Preserve EEPROM on Chip Erase", 1),
        FuseBit(4, "WDTON", "Watchdog Timer Always On", 1),
        FuseBit(5, "SPIEN", "Enable Serial Program and Data Downloading", 0),
        FuseBit(6, "JTAGEN", "Enable JTAG", 0),
        FuseBit(7, "OCDEN", "Enable OCD", 1),
    ]

    usb32u4_ext = [
        FuseBit(0, "BODLEVEL0", "Brown-out Detector trigger level", 1),
        FuseBit(1, "BODLEVEL1", "Brown-out Detector trigger level", 1),
        FuseBit(2, "BODLEVEL2", "Brown-out Detector trigger level", 0),
        FuseBit(3, "HWBE", "Hardware Boot Enable", 0),
        FuseBit(4, "UNIMPLEMENTED", "---", 1),
        FuseBit(5, "UNIMPLEMENTED", "---", 1),
        FuseBit(6, "UNIMPLEMENTED", "---", 1),
        FuseBit(7, "UNIMPLEMENTED", "---", 1),
    ]

    # Additional chips not in original 2014 eXtreme Burner
    additional_chips: Dict[str, AVRChip] = {
        "ATmega328PB": AVRChip("ATmega328PB", 32768, 1024, 128, (0x1E, 0x95, 0x16),
                               default_lfuse=0xFF, default_hfuse=0xDE, default_efuse=0xF7,
                               placement_image=r".\Images\Placements\ZIF_DIP_28.bmp",
                               fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega32U4": AVRChip("ATmega32U4", 32768, 1024, 128, (0x1E, 0x95, 0x87),
                              default_lfuse=0xFF, default_hfuse=0xD8, default_efuse=0xCB,
                              placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                              fuse_layout=_build_layout(std_low_layout2, usb32u4_high, usb32u4_ext)),
        "ATmega16U4": AVRChip("ATmega16U4", 16384, 512, 128, (0x1E, 0x94, 0x88),
                              default_lfuse=0xFF, default_hfuse=0xD9, default_efuse=0xC3,
                              placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                              fuse_layout=_build_layout(std_low_layout2, usb32u4_high, usb32u4_ext)),
        "ATtiny85": AVRChip("ATtiny85", 8192, 512, 64, (0x1E, 0x93, 0x0B), has_efuse=True,
                            default_lfuse=0x62, default_hfuse=0xDF, default_efuse=0xFF,
                            placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                            fuse_layout=_build_layout(tiny_8pin_low, tiny_8pin_high, tiny_8pin_ext)),
        "ATtiny45": AVRChip("ATtiny45", 4096, 256, 64, (0x1E, 0x92, 0x06), has_efuse=True,
                            default_lfuse=0x62, default_hfuse=0xDF, default_efuse=0xFF,
                            placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                            fuse_layout=_build_layout(tiny_8pin_low, tiny_8pin_high, tiny_8pin_ext)),
        "ATtiny25": AVRChip("ATtiny25", 2048, 128, 32, (0x1E, 0x91, 0x08), has_efuse=True,
                            default_lfuse=0x62, default_hfuse=0xDF, default_efuse=0xFF,
                            placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                            fuse_layout=_build_layout(tiny_8pin_low, tiny_8pin_high, tiny_8pin_ext)),
        "ATtiny4313": AVRChip("ATtiny4313", 4096, 256, 64, (0x1E, 0x92, 0x0D), has_efuse=True,
                              default_lfuse=0x64, default_hfuse=0xDF, default_efuse=0xFF,
                              placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                              fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega1280": AVRChip("ATmega1280", 131072, 4096, 256, (0x1E, 0x97, 0x03),
                              default_lfuse=0xFF, default_hfuse=0xDA, default_efuse=0xF5,
                              placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                              fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega1284P": AVRChip("ATmega1284P", 131072, 4096, 256, (0x1E, 0x97, 0x05),
                               default_lfuse=0xFF, default_hfuse=0xDE, default_efuse=0xFD,
                               placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                               fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega644P": AVRChip("ATmega644P", 65536, 2048, 256, (0x1E, 0x96, 0x0A),
                              default_lfuse=0xFF, default_hfuse=0xDE, default_efuse=0xFD,
                              placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                              fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega8A": AVRChip("ATmega8A", 8192, 512, 64, (0x1E, 0x93, 0x07), has_efuse=False,
                            default_lfuse=0xE1, default_hfuse=0xD9,
                            placement_image=r".\Images\Placements\ZIF_DIP_28.bmp",
                            fuse_layout=_build_layout(std_mega_old_low, std_mega_old_high_m8)),
        "ATmega16A": AVRChip("ATmega16A", 16384, 512, 128, (0x1E, 0x94, 0x03), has_efuse=False,
                             default_lfuse=0xE1, default_hfuse=0x99,
                             placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                             fuse_layout=_build_layout(std_mega_old_low, std_mega_old_high_m16_32)),
        "ATmega32A": AVRChip("ATmega32A", 32768, 1024, 128, (0x1E, 0x95, 0x02), has_efuse=False,
                             default_lfuse=0xE1, default_hfuse=0x99,
                             placement_image=r".\Images\Placements\ZIF_DIP_40.bmp",
                             fuse_layout=_build_layout(std_mega_old_low, std_mega_old_high_m16_32)),
        "ATmega88P": AVRChip("ATmega88P", 8192, 512, 64, (0x1E, 0x93, 0x0F),
                             default_lfuse=0x62, default_hfuse=0xDF, default_efuse=0xF9,
                             placement_image=r".\Images\Placements\ZIF_DIP_28.bmp",
                             fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
        "ATmega168P": AVRChip("ATmega168P", 16384, 512, 128, (0x1E, 0x94, 0x0B),
                              default_lfuse=0x62, default_hfuse=0xDF, default_efuse=0xF9,
                              placement_image=r".\Images\Placements\ZIF_DIP_28.bmp",
                              fuse_layout=_build_layout(std_low_layout2, std_high_layout5, std_ext_layout4)),
    }

    for name, chip in additional_chips.items():
        if name not in CHIP_DATABASE:
            CHIP_DATABASE[name] = chip
        elif CHIP_DATABASE[name].fuse_layout is None:
            CHIP_DATABASE[name].fuse_layout = chip.fuse_layout

    # Update placement images on common chips if missing
    for name, chip in CHIP_DATABASE.items():
        if not chip.placement_image:
            if "328" in name or "168" in name or "88" in name or "48" in name or "8" in name:
                chip.placement_image = r".\Images\Placements\ZIF_DIP_28.bmp"
            elif "16" in name or "32" in name or "64" in name or "128" in name or "256" in name:
                chip.placement_image = r".\Images\Placements\ZIF_DIP_40.bmp"
            elif "tiny" in name.lower():
                chip.placement_image = r".\Images\Placements\ZIF_DIP_40.bmp"

# Auto-initialize on import
init_chip_database()

def find_by_signature(sig: Tuple[int, int, int]) -> Optional[AVRChip]:
    """Finds chip by 3-byte signature tuple (e.g. (0x1E, 0x95, 0x0F))."""
    for chip in CHIP_DATABASE.values():
        if chip.signature == sig:
            return chip
    return None

def find_by_name(name: str) -> Optional[AVRChip]:
    """Finds chip by name (case-insensitive and alias matching)."""
    clean_name = name.lower().strip()
    for k, chip in CHIP_DATABASE.items():
        if k.lower() == clean_name:
            return chip
        # Handle slash-separated aliases like ATmega168/ATmega168V/ATmega168A
        aliases = [a.lower().strip() for a in k.split('/')]
        if clean_name in aliases:
            return chip
    return None

def get_all_chip_names() -> List[str]:
    """Returns sorted list of all supported chip names."""
    return sorted(list(CHIP_DATABASE.keys()))
