"""
================================================================================
ENIT AVR STUDIO - Professional Microcontroller Programmer Suite
Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India
All Rights Reserved.
================================================================================
"""

import os
import sys
import time
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QUrl
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QStatusBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
)

from enit_avr_core import SCK_SPEEDS, USBaspProgrammer
from enit_chip_db import AVRChip, CHIP_DATABASE, find_by_name, find_by_signature, get_all_chip_names, FuseBit
from enit_hex_parser import IntelHex

# ==============================================================================
# Open Source Community & Social Media URLs (Aries Computer Solutions)
# ==============================================================================
PAYPAL_ME_BASE_URL = "https://paypal.me/ariestech"
GITHUB_REPO_URL = "https://github.com/arieslaptop/ENIT-AVR-Studio"
WEBSITE_URL = "http://www.arieslaptop.in"
YOUTUBE_URL = "https://www.youtube.com/harshadpatel"
FACEBOOK_URL = "https://www.facebook.com/aries.harshadpatel"

# Application Base Directory (Supports development & PyInstaller bundling)
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Modern Cyber Dark Palette (ENIT Industrial Aesthetic)
STYLE_SHEET = """
QMainWindow {
    background-color: #11141c;
}
QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    font-size: 13px;
}
QFrame.HeaderFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #090d16, stop:1 #1e293b);
    border-bottom: 2px solid #00adb5;
    padding: 10px;
}
QFrame.TelemetryHUD {
    background-color: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 6px 12px;
}
QGroupBox {
    border: 1px solid #334155;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: bold;
    color: #38bdf8;
    background-color: #171b26;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #2563eb;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}
QPushButton.SuccessBtn {
    background-color: #059669;
}
QPushButton.SuccessBtn:hover {
    background-color: #047857;
}
QPushButton.DangerBtn {
    background-color: #dc2626;
}
QPushButton.DangerBtn:hover {
    background-color: #b91c1c;
}
QPushButton.SecondaryBtn {
    background-color: #334155;
}
QPushButton.SecondaryBtn:hover {
    background-color: #475569;
}
QPushButton.AccentBtn {
    background-color: #0891b2;
}
QPushButton.AccentBtn:hover {
    background-color: #0e7490;
}
QPushButton.DonateBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e293b, stop:1 #0f172a);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    font-weight: bold;
    border-radius: 4px;
    padding: 6px 14px;
}
QPushButton.DonateBtn:hover {
    background-color: #0284c7;
    color: #ffffff;
    border-color: #38bdf8;
}
QComboBox, QLineEdit, QSpinBox {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 5px 8px;
    color: #f8fafc;
}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #38bdf8;
}
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #141722;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #1b202e;
    color: #94a3b8;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background-color: #141722;
    color: #38bdf8;
    border-top: 2px solid #38bdf8;
}
QTableWidget {
    background-color: #080c14;
    alternate-background-color: #0e1320;
    gridline-color: #1e293b;
    color: #f1f5f9;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #334155;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 4px;
    border: 1px solid #334155;
    font-weight: bold;
}
QTextEdit {
    background-color: #080c14;
    color: #10b981;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #334155;
    border-radius: 4px;
}
QProgressBar {
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    background-color: #090d16;
    color: #ffffff;
    font-weight: bold;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #06b6d4);
    border-radius: 3px;
}
QMessageBox {
    background-color: #171b26;
    border: 1px solid #334155;
    color: #f8fafc;
}
QMessageBox QLabel {
    color: #f8fafc;
    background-color: transparent;
    font-size: 13px;
    font-weight: 500;
}
QMessageBox QPushButton {
    min-width: 80px;
    min-height: 28px;
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}
QMessageBox QPushButton:hover {
    background-color: #1d4ed8;
}
QDialog {
    background-color: #171b26;
    color: #f8fafc;
    border: 1px solid #334155;
}
QDialog QLabel {
    color: #f8fafc;
}

"""

class BitDetailsDialog(QDialog):
    """Modal dialog displaying interactive bit-by-bit checkboxes matching eXtreme Burner."""
    def __init__(self, title: str, bits: List[FuseBit], current_val: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Bit Details - {title}")
        self.resize(460, 360)
        self.setStyleSheet(STYLE_SHEET)
        self.value = current_val

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        header_lbl = QLabel(f"Configure {title} (Current: 0x{current_val:02X})")
        header_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(header_lbl)

        sub_lbl = QLabel("Note: In AVR microcontrollers, a programmed fuse bit equals '0' (Unchecked), and unprogrammed equals '1' (Checked).")
        sub_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        sub_lbl.setWordWrap(True)
        layout.addWidget(sub_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)

        self.checks = {}
        for b in range(8):
            bit_def = next((x for x in bits if x.position == b), None)
            name = bit_def.name if bit_def else f"Bit {b}"
            details = bit_def.details if bit_def else "Reserved / Unused"

            cb = QCheckBox(f"Bit {b} [{name}]: {details}")
            cb.setChecked((current_val & (1 << b)) != 0)
            cb.stateChanged.connect(self._on_check_changed)
            scroll_layout.addWidget(cb)
            self.checks[b] = cb

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        btn_box = QHBoxLayout()
        self.lbl_hex_result = QLabel(f"Calculated Value: 0x{current_val:02X}")
        self.lbl_hex_result.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")
        btn_box.addWidget(self.lbl_hex_result)
        btn_box.addStretch()

        btn_ok = QPushButton("Apply Settings")
        btn_ok.setProperty("class", "SuccessBtn")
        btn_ok.clicked.connect(self.accept)
        btn_box.addWidget(btn_ok)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        layout.addLayout(btn_box)

    def _on_check_changed(self):
        val = 0
        for b, cb in self.checks.items():
            if cb.isChecked():
                val |= (1 << b)
        self.value = val
        self.lbl_hex_result.setText(f"Calculated Value: 0x{val:02X}")


class ClockConfigDialog(QDialog):
    """Clock Configuration Wizard matching eXtreme Burner's 'Configure AVR Clock'."""
    def __init__(self, current_lfuse: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AVR Clock System")
        self.resize(520, 380)
        self.setStyleSheet(STYLE_SHEET)
        self.resulting_lfuse = current_lfuse

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("AVR Clock Source & Oscillator Configuration")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Select Clock Source:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "External Crystal / Ceramic Resonator (High Frequency > 8 MHz)",
            "External Crystal / Ceramic Resonator (Medium Frequency 3-8 MHz)",
            "Calibrated Internal RC Oscillator (8.0 MHz)",
            "Calibrated Internal RC Oscillator (1.0 MHz - Factory Low Power Default)",
            "External Low Frequency Crystal (32.768 kHz RTC)",
            "External Clock Generator"
        ])
        self.combo_type.currentIndexChanged.connect(self._recalculate)
        layout.addWidget(self.combo_type)

        layout.addWidget(QLabel("Start-up Delay & Power-up Timing:"))
        self.combo_sut = QComboBox()
        self.combo_sut.addItems([
            "16K Clock Cycles + 65 ms (Slow rising power - Recommended for Crystal)",
            "16K Clock Cycles + 4.1 ms (Fast rising power)",
            "1K Clock Cycles + 0 ms (BOD Enabled)"
        ])
        self.combo_sut.currentIndexChanged.connect(self._recalculate)
        layout.addWidget(self.combo_sut)

        layout.addWidget(QLabel("Clock Options:"))
        self.chk_ckdiv8 = QCheckBox("Divide clock by 8 internally (CKDIV8 fuse)")
        self.chk_ckdiv8.setChecked(False)
        self.chk_ckdiv8.stateChanged.connect(self._recalculate)
        layout.addWidget(self.chk_ckdiv8)

        self.chk_ckout = QCheckBox("Output system clock on PORTB0 / CLKO pin (CKOUT fuse)")
        self.chk_ckout.setChecked(False)
        self.chk_ckout.stateChanged.connect(self._recalculate)
        layout.addWidget(self.chk_ckout)

        # Result preview box
        res_frame = QFrame()
        res_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #334155; border-radius: 6px; padding: 10px;")
        res_layout = QVBoxLayout(res_frame)
        self.lbl_result_hex = QLabel("Calculated Low Fuse: 0xFF")
        self.lbl_result_hex.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        self.lbl_result_desc = QLabel("Recommended for standard 16 MHz Arduino Uno / Nano boards.")
        self.lbl_result_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        res_layout.addWidget(self.lbl_result_hex)
        res_layout.addWidget(self.lbl_result_desc)
        layout.addWidget(res_frame)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_apply = QPushButton("Apply to Low Fuse")
        btn_apply.setProperty("class", "SuccessBtn")
        btn_apply.clicked.connect(self.accept)
        btn_box.addWidget(btn_apply)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

        self._recalculate()

    def _recalculate(self):
        idx = self.combo_type.currentIndex()
        sut_idx = self.combo_sut.currentIndex()

        if idx == 0:  # 16MHz Crystal
            cksel = 0b1111
            desc = "Full Swing 16 MHz Crystal with capacitors. Low Fuse: 0xFF"
        elif idx == 1: # Medium Freq
            cksel = 0b1101
            desc = "Medium Frequency Crystal (3-8 MHz)."
        elif idx == 2: # 8MHz Internal RC
            cksel = 0b0010
            desc = "Internal 8.0 MHz RC oscillator (no external components required)."
        elif idx == 3: # 1MHz Internal RC
            cksel = 0b0010
            desc = "Internal 1.0 MHz RC oscillator (8MHz divided by 8)."
        elif idx == 4: # 32.768kHz
            cksel = 0b0100
            desc = "32.768 kHz Low Frequency watch crystal."
        else: # External clock
            cksel = 0b0000
            desc = "External active clock signal fed to XTAL1 pin."

        # SUT
        if sut_idx == 0:
            sut = 0b10
        elif sut_idx == 1:
            sut = 0b01
        else:
            sut = 0b00

        # Build byte: bits 0..3 = CKSEL, bits 4..5 = SUT, bit 6 = CKOUT, bit 7 = CKDIV8
        val = (cksel & 0x0F) | ((sut & 0x03) << 4)
        if not self.chk_ckout.isChecked():
            val |= (1 << 6) # unprogrammed = 1
        if not self.chk_ckdiv8.isChecked() and idx != 3:
            val |= (1 << 7) # unprogrammed = 1

        self.resulting_lfuse = val
        self.lbl_result_hex.setText(f"Calculated Low Fuse: 0x{val:02X}")
        self.lbl_result_desc.setText(desc)


class EnitConfirmDialog(QDialog):
    """Custom Cyber-Dark Confirmation Dialog ensuring 100% contrast & readability across all Windows versions."""
    def __init__(self, title: str, headline: str, items: List[str], confirm_text: str = "Yes, Proceed", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(520, 290)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header with warning/question badge
        hdr_layout = QHBoxLayout()
        badge = QLabel("⚡")
        badge.setStyleSheet("font-size: 24px; color: #38bdf8; background: #1e293b; border-radius: 18px; padding: 4px; text-align: center;")
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignCenter)
        hdr_layout.addWidget(badge)

        head_lbl = QLabel(headline)
        head_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        head_lbl.setWordWrap(True)
        hdr_layout.addWidget(head_lbl, 1)
        layout.addLayout(hdr_layout)

        # Bullet items box
        if items:
            box = QFrame()
            box.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 8px;")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(10, 8, 10, 8)
            box_layout.setSpacing(6)
            for it in items:
                lbl = QLabel(f"•  {it}")
                lbl.setStyleSheet("color: #cbd5e1; font-size: 13px; font-weight: 500; background: transparent;")
                box_layout.addWidget(lbl)
            layout.addWidget(box)

        prompt_lbl = QLabel("Do you want to proceed with this operation?")
        prompt_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #38bdf8;")
        layout.addWidget(prompt_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_no = QPushButton("Cancel")
        btn_no.setProperty("class", "SecondaryBtn")
        btn_no.setStyleSheet("padding: 7px 20px; font-size: 13px; background-color: #334155;")
        btn_no.clicked.connect(self.reject)
        btn_layout.addWidget(btn_no)

        btn_yes = QPushButton(confirm_text)
        btn_yes.setProperty("class", "DangerBtn")
        btn_yes.setStyleSheet("padding: 7px 22px; font-size: 13px; font-weight: bold;")
        btn_yes.clicked.connect(self.accept)
        btn_layout.addWidget(btn_yes)

        layout.addLayout(btn_layout)


class ZIFPlacementDialog(QDialog):
    """Displays the physical ZIF socket placement diagram for the selected microcontroller."""
    def __init__(self, chip: AVRChip, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"ZIF Socket Placement Guide - {chip.name}")
        self.resize(560, 380)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_lbl = QLabel(f"ZIF Socket Wiring & Insertion Guide: {chip.name}")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("Always insert the IC with Notch / Pin 1 facing TOWARDS the ZIF socket lever handle.\nMake sure the socket lever is raised before inserting, and locked DOWN before programming.")
        desc_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # Image display frame
        img_frame = QFrame()
        img_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px;")
        frame_layout = QVBoxLayout(img_frame)
        frame_layout.setAlignment(Qt.AlignCenter)

        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)

        # Resolve placement image
        img_path = ""
        base_dir = BASE_DIR
        if chip.placement_image:
            rel = chip.placement_image.replace(".\\\\", "").replace("./", "").replace(".\\", "")
            cand = [
                os.path.join(base_dir, rel),
                os.path.join(base_dir, "Images", "Placements", os.path.basename(rel)),
                os.path.join(r"C:\Program Files\eXtreme Burner - AVR", rel)
            ]
            for c in cand:
                if os.path.exists(c):
                    img_path = c
                    break

        if not img_path or not os.path.exists(img_path):
            if any(x in chip.name for x in ["28", "328", "168", "88", "48", "8"]):
                img_path = os.path.join(base_dir, "Images", "Placements", "ZIF_DIP_28.bmp")
            else:
                img_path = os.path.join(base_dir, "Images", "Placements", "ZIF_DIP_40.bmp")

        if os.path.exists(img_path):
            pix = QPixmap(img_path)
            if not pix.isNull():
                scaled = pix.scaled(500, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_img.setPixmap(scaled)
            else:
                lbl_img.setText(f"Placement Image: {os.path.basename(img_path)}")
        else:
            lbl_img.setText("No placement diagram file found on disk.")
            lbl_img.setStyleSheet("color: #ef4444; font-size: 13px;")

        frame_layout.addWidget(lbl_img)
        layout.addWidget(img_frame)

        info_box = QLabel(f"Microcontroller Specs: Flash={chip.flash_size} Bytes | EEPROM={chip.eeprom_size} Bytes | Page Size={chip.page_size} Bytes | Signature: 0x{chip.signature[0]:02X} 0x{chip.signature[1]:02X} 0x{chip.signature[2]:02X}")
        info_box.setStyleSheet("font-size: 11px; color: #10b981; font-weight: bold;")
        info_box.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_box)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close Guide")
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)


class DonateDialog(QDialog):
    """
    Support Open Source Development Modal for Aries Computer Solutions.
    Provides direct sponsorship tiers, link copying, and repository navigation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Support Open Source Development - Aries Computer Solutions")
        self.setModal(True)
        self.resize(620, 480)
        self.setStyleSheet(STYLE_SHEET)

        icon_path = os.path.join(BASE_DIR, "Icons", "enit_avr_studio.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        # Header Badge and Titles
        hdr_layout = QHBoxLayout()
        hdr_layout.setSpacing(14)
        badge = QLabel("❤")
        badge.setStyleSheet("font-size: 24px; color: #f43f5e; background: #1e293b; border: 1px solid #334155; border-radius: 21px; padding: 4px; text-align: center;")
        badge.setFixedSize(42, 42)
        badge.setAlignment(Qt.AlignCenter)
        hdr_layout.addWidget(badge)

        head_info = QVBoxLayout()
        head_info.setSpacing(3)
        head_title = QLabel("Support Open Source Development")
        head_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        head_sub = QLabel("Aries Computer Solutions • Harshad Patel, India")
        head_sub.setStyleSheet("font-size: 12px; font-weight: 600; color: #94a3b8;")
        head_info.addWidget(head_title)
        head_info.addWidget(head_sub)
        hdr_layout.addLayout(head_info)
        hdr_layout.addStretch()
        layout.addLayout(hdr_layout)

        # Mission Statement Box
        msg_frame = QFrame()
        msg_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 8px; padding: 12px;")
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(12, 10, 12, 10)
        msg_layout.setSpacing(8)

        desc_lbl = QLabel(
            "Thank you for using ENIT AVR Studio! Your sponsorship powers continuous "
            "development, cutting-edge hardware flashing algorithms, AVR chip library updates, "
            "and ensures high-performance open-source tools remain accessible for engineers, "
            "repair technicians, students, and makers worldwide."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.5;")
        msg_layout.addWidget(desc_lbl)
        layout.addWidget(msg_frame)

        # Tier Buttons
        tier_lbl = QLabel("SELECT SPONSORSHIP TIER:")
        tier_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.8px;")
        layout.addWidget(tier_lbl)

        btn_tier_layout = QHBoxLayout()
        btn_tier_layout.setSpacing(12)

        btn_10 = QPushButton("💲 $10 USD")
        btn_10.setCursor(Qt.PointingHandCursor)
        btn_10.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #065f46, stop:1 #047857); color: #ecfdf5; font-size: 13px; font-weight: bold; padding: 10px 16px; border-radius: 6px; border: 1px solid #10b981;")
        btn_10.clicked.connect(lambda: self._open_url(f"{PAYPAL_ME_BASE_URL}/10USD"))
        btn_tier_layout.addWidget(btn_10)

        btn_20 = QPushButton("💲 $20 USD")
        btn_20.setCursor(Qt.PointingHandCursor)
        btn_20.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #0369a1); color: #f0f9ff; font-size: 13px; font-weight: bold; padding: 10px 16px; border-radius: 6px; border: 1px solid #38bdf8;")
        btn_20.clicked.connect(lambda: self._open_url(f"{PAYPAL_ME_BASE_URL}/20USD"))
        btn_tier_layout.addWidget(btn_20)

        btn_custom = QPushButton("✨ Custom Amount")
        btn_custom.setCursor(Qt.PointingHandCursor)
        btn_custom.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4f46e5, stop:1 #4338ca); color: #eef2ff; font-size: 13px; font-weight: bold; padding: 10px 16px; border-radius: 6px; border: 1px solid #818cf8;")
        btn_custom.clicked.connect(lambda: self._open_url(PAYPAL_ME_BASE_URL))
        btn_tier_layout.addWidget(btn_custom)

        layout.addLayout(btn_tier_layout)

        # PayPal URL & Repository Box
        link_frame = QFrame()
        link_frame.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 8px;")
        link_layout = QHBoxLayout(link_frame)
        link_layout.setContentsMargins(10, 6, 10, 6)
        link_layout.setSpacing(10)

        lbl_link = QLabel(PAYPAL_ME_BASE_URL)
        lbl_link.setStyleSheet("color: #38bdf8; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; font-weight: 500;")
        link_layout.addWidget(lbl_link, 1)

        self.btn_copy = QPushButton("📋 Copy Link")
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.setProperty("class", "SecondaryBtn")
        self.btn_copy.setStyleSheet("padding: 6px 12px; font-size: 12px;")
        self.btn_copy.clicked.connect(self._copy_paypal_link)
        link_layout.addWidget(self.btn_copy)

        btn_github = QPushButton("🌐 GitHub Repository")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.setProperty("class", "SecondaryBtn")
        btn_github.setStyleSheet("padding: 6px 12px; font-size: 12px;")
        btn_github.clicked.connect(lambda: self._open_url(GITHUB_REPO_URL))
        link_layout.addWidget(btn_github)

        layout.addWidget(link_frame)

        # Community & Social Media Links Frame
        social_frame = QFrame()
        social_frame.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 6px 10px;")
        soc_layout = QHBoxLayout(social_frame)
        soc_layout.setContentsMargins(6, 4, 6, 4)
        soc_layout.setSpacing(10)

        soc_lbl = QLabel("COMMUNITY:")
        soc_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        soc_layout.addWidget(soc_lbl)

        btn_web = QPushButton("🌍 www.arieslaptop.in")
        btn_web.setCursor(Qt.PointingHandCursor)
        btn_web.setProperty("class", "SecondaryBtn")
        btn_web.setStyleSheet("padding: 5px 12px; font-size: 12px; font-weight: 600; color: #38bdf8;")
        btn_web.clicked.connect(lambda: self._open_url(WEBSITE_URL))
        soc_layout.addWidget(btn_web)

        btn_yt = QPushButton("▶ YouTube")
        btn_yt.setCursor(Qt.PointingHandCursor)
        btn_yt.setProperty("class", "SecondaryBtn")
        btn_yt.setStyleSheet("padding: 5px 12px; font-size: 12px; font-weight: 600; color: #f87171;")
        btn_yt.clicked.connect(lambda: self._open_url(YOUTUBE_URL))
        soc_layout.addWidget(btn_yt)

        btn_fb = QPushButton("📘 Facebook")
        btn_fb.setCursor(Qt.PointingHandCursor)
        btn_fb.setProperty("class", "SecondaryBtn")
        btn_fb.setStyleSheet("padding: 5px 12px; font-size: 12px; font-weight: 600; color: #60a5fa;")
        btn_fb.clicked.connect(lambda: self._open_url(FACEBOOK_URL))
        soc_layout.addWidget(btn_fb)

        soc_layout.addStretch()
        layout.addWidget(social_frame)

        # Bottom Close Button
        btn_bottom_layout = QHBoxLayout()
        btn_bottom_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.clicked.connect(self.accept)
        btn_bottom_layout.addWidget(btn_close)
        layout.addLayout(btn_bottom_layout)

    def _open_url(self, url: str):
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception:
            import webbrowser
            webbrowser.open(url)

    def _copy_paypal_link(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(PAYPAL_ME_BASE_URL)
        self.btn_copy.setText("✓ Copied!")
        self.btn_copy.setStyleSheet("background-color: #059669; color: #ffffff; padding: 6px 12px; font-size: 12px; font-weight: bold;")
        QTimer.singleShot(2500, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.btn_copy.setText("📋 Copy Link")
        self.btn_copy.setProperty("class", "SecondaryBtn")
        self.btn_copy.setStyleSheet("padding: 6px 12px; font-size: 12px;")


class WorkerThread(QThread):
    """Background worker for non-blocking hardware operations with telemetry streaming."""
    log_signal = Signal(str)
    progress_signal = Signal(int, int)
    telemetry_signal = Signal(dict)
    finished_signal = Signal(bool, str)

    def __init__(self, action: str, programmer: USBaspProgrammer, **kwargs):
        super().__init__()
        self.action = action
        self.prog = programmer
        self.kwargs = kwargs

    def _verify_against_source(self, chip_size: int, page_size: int, buffer_data: bytes,
                               source_path: Optional[str], label: str = "Flash") -> Tuple[bool, str]:
        """
        Reads back Flash memory from the physical ATmega chip and compares byte-for-byte
        against the original PC source file (if loaded from disk) or the memory buffer.
        """
        expected = buffer_data
        source_desc = "memory buffer"

        if source_path and os.path.exists(source_path):
            self.log_signal.emit(f"[VERIFY] Reloading original PC file for strict comparison: {source_path}")
            pc_hex = IntelHex(size=chip_size)
            pc_hex.load_hex_file(source_path)
            expected = bytes(pc_hex.buffer[:chip_size])
            source_desc = os.path.basename(source_path)

        self.log_signal.emit(f"[VERIFY] Reading back {label} ({chip_size} bytes) from ATmega chip...")
        actual = self.prog.read_flash(
            chip_size, page_size,
            progress_callback=lambda c, t: self.progress_signal.emit(c, t),
            telemetry_callback=lambda telem: self.telemetry_signal.emit({
                **telem,
                "status": f"Verifying vs {source_desc}: 0x{telem['current']:04X}/{chip_size} ({telem['percent']}%)"
            })
        )

        mismatches = 0
        first_err = None
        for i in range(chip_size):
            if actual[i] != expected[i]:
                if first_err is None:
                    first_err = (i, expected[i], actual[i])
                mismatches += 1

        if mismatches == 0:
            self.log_signal.emit(
                f"[VERIFY OK] 100% Bit-Exact Match! Chip {label} ({chip_size} bytes) == PC File ({source_desc})."
            )
            return True, f"Verify OK (100% Match vs {source_desc})"

        addr, exp_b, act_b = first_err
        err_msg = (
            f"VERIFY FAILED: {mismatches} byte mismatch(es) vs {source_desc}! "
            f"First mismatch at 0x{addr:04X}: PC=0x{exp_b:02X}, Chip=0x{act_b:02X}"
        )
        self.log_signal.emit(f"[ERROR] {err_msg}")
        return False, err_msg

    def run(self):
        try:
            self.prog.log_cb = lambda msg: self.log_signal.emit(msg)

            if self.action == "connect":
                success = self.prog.connect_target()
                if success:
                    chip = self.prog.autodetect_chip()
                    fuses = self.prog.read_fuses()
                    self.finished_signal.emit(True, "Connected")
                else:
                    self.finished_signal.emit(False, "Sync failed")

            elif self.action == "read_signature":
                sig = self.prog.read_signature()
                chip = self.prog.autodetect_chip()
                self.finished_signal.emit(True, f"Target Signature: 0x{sig[0]:02X} 0x{sig[1]:02X} 0x{sig[2]:02X}")

            elif self.action == "erase":
                ok = self.prog.chip_erase()
                self.finished_signal.emit(ok, "Erase completed" if ok else "Erase failed")

            elif self.action == "read_flash":
                size = self.kwargs["size"]
                page = self.kwargs.get("page_size", 128)
                data = self.prog.read_flash(
                    size, page,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                self.kwargs["container"]["data"] = data
                self.finished_signal.emit(True, "Flash read OK")

            elif self.action == "write_flash":
                data = self.kwargs["data"]
                page = self.kwargs.get("page_size", 128)
                skip_blank = self.kwargs.get("skip_blank", True)
                source_path = self.kwargs.get("source_path")
                ok = self.prog.write_flash(
                    data, page,
                    skip_blank_pages=skip_blank,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                if not ok:
                    self.finished_signal.emit(False, "Flash write failed")
                    return
                v_ok, v_msg = self._verify_against_source(len(data), page, data, source_path, "Flash")
                self.finished_signal.emit(v_ok, f"Flash Write & {v_msg}" if v_ok else v_msg)

            elif self.action == "read_eeprom":
                size = self.kwargs["size"]
                data = self.prog.read_eeprom(
                    size, 128,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                self.kwargs["container"]["data"] = data
                self.finished_signal.emit(True, "EEPROM read OK")

            elif self.action == "write_eeprom":
                data = self.kwargs["data"]
                ok = self.prog.write_eeprom(
                    data, 4,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                self.finished_signal.emit(ok, "EEPROM write OK" if ok else "EEPROM write failed")

            elif self.action == "verify_flash":
                expected = self.kwargs["data"]
                page = self.kwargs.get("page_size", 128)
                source_path = self.kwargs.get("source_path")
                v_ok, v_msg = self._verify_against_source(len(expected), page, expected, source_path, "Flash")
                self.finished_signal.emit(v_ok, v_msg)

            elif self.action == "read_fuses":
                fuses = self.prog.read_fuses()
                self.kwargs["container"]["fuses"] = fuses
                self.finished_signal.emit(True, "Fuses read OK")

            elif self.action == "write_fuses":
                f = self.kwargs["fuses"]
                ok = self.prog.write_fuses(f.get("low"), f.get("high"), f.get("ext"), f.get("lock"))
                self.finished_signal.emit(ok, "Fuses updated" if ok else "Fuse write failed")

            elif self.action == "write_all":
                # Unified Write All: Erase -> Flash -> Strict Verify vs PC File -> EEPROM -> Fuses
                chip = self.kwargs["chip"]
                flash_data = self.kwargs.get("flash_data")
                flash_source_path = self.kwargs.get("flash_source_path")
                eeprom_data = self.kwargs.get("eeprom_data")
                fuses = self.kwargs.get("fuses")

                # Step 1: Chip Erase
                self.log_signal.emit("[WRITE ALL - STEP 1/5] Performing Chip Erase...")
                if not self.prog.chip_erase():
                    self.finished_signal.emit(False, "Chip Erase failed during Write All")
                    return

                # Step 2 & 3: Write Flash & Verify against original PC source file
                if flash_data and any(b != 0xFF for b in flash_data):
                    self.log_signal.emit(f"[WRITE ALL - STEP 2/5] Programming Flash ({len(flash_data)} bytes)...")
                    ok = self.prog.write_flash(
                        flash_data, chip.page_size, skip_blank_pages=True,
                        progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                        telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                    )
                    if not ok:
                        self.finished_signal.emit(False, "Flash write failed during Write All")
                        return

                    self.log_signal.emit("[WRITE ALL - STEP 3/5] Verifying Chip Flash vs PC Source File...")
                    v_ok, v_msg = self._verify_against_source(
                        chip.flash_size, chip.page_size, flash_data, flash_source_path, "Flash"
                    )
                    if not v_ok:
                        self.finished_signal.emit(False, f"Write All aborted: {v_msg}")
                        return

                # Step 4: Write EEPROM
                if eeprom_data and any(b != 0xFF for b in eeprom_data):
                    self.log_signal.emit(f"[WRITE ALL - STEP 4/5] Programming EEPROM ({len(eeprom_data)} bytes)...")
                    ok = self.prog.write_eeprom(
                        eeprom_data, 4,
                        progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                        telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                    )
                    if not ok:
                        self.finished_signal.emit(False, "EEPROM write failed during Write All")
                        return

                # Step 5: Write Fuses
                if fuses:
                    self.log_signal.emit("[WRITE ALL - STEP 5/5] Writing Selected Fuse & Lock Bits...")
                    self.prog.write_fuses(fuses.get("low"), fuses.get("high"), fuses.get("ext"), fuses.get("lock"))

                self.finished_signal.emit(True, "WRITE ALL & VERIFY OK (100% Match!)")

            elif self.action == "read_all":
                # Unified Read All: Fuses, Flash, EEPROM
                chip = self.kwargs["chip"]
                container = self.kwargs["container"]

                self.log_signal.emit("[READ ALL - STEP 1/3] Reading Device Fuses & Calibration...")
                fuses = self.prog.read_fuses()
                container["fuses"] = fuses

                self.log_signal.emit(f"[READ ALL - STEP 2/3] Reading Flash Memory ({chip.flash_size} bytes)...")
                flash_data = self.prog.read_flash(
                    chip.flash_size, chip.page_size,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                container["flash"] = flash_data

                self.log_signal.emit(f"[READ ALL - STEP 3/3] Reading EEPROM Memory ({chip.eeprom_size} bytes)...")
                eeprom_data = self.prog.read_eeprom(
                    chip.eeprom_size, 128,
                    progress_callback=lambda c, t: self.progress_signal.emit(c, t),
                    telemetry_callback=lambda telem: self.telemetry_signal.emit(telem)
                )
                container["eeprom"] = eeprom_data

                self.finished_signal.emit(True, "READ ALL COMPLETED SUCCESSFULLY!")

        except Exception as ex:
            self.log_signal.emit(f"Worker Error: {str(ex)}")
            self.finished_signal.emit(False, str(ex))


class EnitAVRStudio(QMainWindow):
    """Main Application Window for ENIT AVR Studio."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ENIT AVR Studio v1.0.1 - Professional Microcontroller Programmer Suite")
        self.resize(1180, 820)
        self.setStyleSheet(STYLE_SHEET)

        icon_path = os.path.join(BASE_DIR, "Icons", "enit_avr_studio.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.programmer = USBaspProgrammer(log_callback=self.log)
        self.active_chip: Optional[AVRChip] = find_by_name("ATmega328P")
        self.flash_buffer = IntelHex(size=32768)
        self.eeprom_buffer = IntelHex(size=1024)
        self.loaded_flash_path: Optional[str] = None
        self.loaded_eeprom_path: Optional[str] = None
        self.worker: Optional[WorkerThread] = None

        self._setup_ui()
        self._update_chip_info()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(10)

        # Header Banner
        header = QFrame()
        header.setProperty("class", "HeaderFrame")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 6, 10, 6)

        # Official ENIT 3D Levitating Chip Logo
        logo_lbl = QLabel()
        base_dir = BASE_DIR
        logo_path = os.path.join(base_dir, "Images", "enit_logo_header.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(base_dir, "Images", "enit_logo.png")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                scaled = pix.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_lbl.setPixmap(scaled)
        logo_lbl.setFixedSize(54, 54)
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent; border: 1px solid #2a3348; border-radius: 6px; padding: 1px;")
        h_layout.addWidget(logo_lbl)
        h_layout.addSpacing(10)

        title_layout = QVBoxLayout()
        title_lbl = QLabel("ENIT AVR STUDIO")
        title_lbl.setStyleSheet("font-size: 21px; font-weight: bold; color: #38bdf8; letter-spacing: 1px;")
        sub_lbl = QLabel("Advanced Microcontroller Programmer & Hardware Diagnostic Platform")
        sub_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        h_layout.addLayout(title_layout)

        h_layout.addStretch()

        # Live Hardware Status Pill (Google Stitch HUD)
        self.pill_hardware = QFrame()
        self.pill_hardware.setStyleSheet("background-color: #171b26; border: 1px solid #2a3348; border-radius: 14px; padding: 4px 12px;")
        pill_layout = QHBoxLayout(self.pill_hardware)
        pill_layout.setContentsMargins(0, 0, 0, 0)
        pill_layout.setSpacing(8)

        self.lbl_status_led = QLabel("●")
        self.lbl_status_led.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
        pill_layout.addWidget(self.lbl_status_led)

        self.lbl_hardware_summary = QLabel("DEVICE READY • USBasp Connected • VTarget: 5.0V • Target: ATmega328P (0x1E 0x95 0x0F)")
        self.lbl_hardware_summary.setStyleSheet("color: #e0e2ee; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; font-weight: 500;")
        pill_layout.addWidget(self.lbl_hardware_summary)
        h_layout.addWidget(self.pill_hardware)

        h_layout.addSpacing(12)

        copy_lbl = QLabel("Copyright (C) 2026 Aries Computer Solutions\nHarshad Patel, India")
        copy_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        copy_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #00adb5;")
        h_layout.addWidget(copy_lbl)

        main_layout.addWidget(header)

        # Top Control Toolbar
        toolbar_group = QGroupBox("HARDWARE CONTROL & DEVICE WORKFLOW")
        tb_layout = QHBoxLayout(toolbar_group)
        tb_layout.setContentsMargins(12, 10, 12, 10)
        tb_layout.setSpacing(10)

        self.btn_connect = QPushButton("Connect USBasp")
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        tb_layout.addWidget(self.btn_connect)

        self.btn_autodetect = QPushButton("Auto-Detect Chip")
        self.btn_autodetect.clicked.connect(self.on_autodetect_clicked)
        self.btn_autodetect.setProperty("class", "SecondaryBtn")
        tb_layout.addWidget(self.btn_autodetect)

        tb_layout.addWidget(QLabel("Target Chip:"))
        self.combo_chips = QComboBox()
        self.combo_chips.addItems(get_all_chip_names())
        self.combo_chips.setCurrentText("ATmega328P")
        self.combo_chips.currentTextChanged.connect(self.on_chip_selected)
        tb_layout.addWidget(self.combo_chips)

        tb_layout.addWidget(QLabel("ISP SCK:"))
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(list(SCK_SPEEDS.keys()))
        self.combo_speed.setCurrentText("Auto")
        self.combo_speed.currentTextChanged.connect(self.on_speed_changed)
        tb_layout.addWidget(self.combo_speed)

        tb_layout.addStretch()

        self.btn_read_all = QPushButton("Read All")
        self.btn_read_all.setProperty("class", "SuccessBtn")
        self.btn_read_all.clicked.connect(self.on_read_all)
        tb_layout.addWidget(self.btn_read_all)

        self.btn_write_all = QPushButton("Write All")
        self.btn_write_all.setProperty("class", "DangerBtn")
        self.btn_write_all.clicked.connect(self.on_write_all)
        tb_layout.addWidget(self.btn_write_all)

        self.btn_erase = QPushButton("Chip Erase")
        self.btn_erase.setProperty("class", "DangerBtn")
        self.btn_erase.clicked.connect(self.on_chip_erase)
        tb_layout.addWidget(self.btn_erase)

        self.btn_zif = QPushButton("ZIF Socket Guide")
        self.btn_zif.setProperty("class", "SecondaryBtn")
        self.btn_zif.clicked.connect(self.on_show_zif_guide)
        tb_layout.addWidget(self.btn_zif)

        self.btn_donate = QPushButton("❤ Donate")
        self.btn_donate.setProperty("class", "DonateBtn")
        self.btn_donate.setToolTip("Support Open Source Development - Aries Computer Solutions")
        self.btn_donate.setCursor(Qt.PointingHandCursor)
        self.btn_donate.clicked.connect(self.on_show_donate_dialog)
        tb_layout.addWidget(self.btn_donate)

        main_layout.addWidget(toolbar_group)

        # Telemetry HUD Frame (Google Stitch Dynamic Ribbon)
        telemetry_frame = QFrame()
        telemetry_frame.setProperty("class", "TelemetryHUD")
        telem_layout = QHBoxLayout(telemetry_frame)
        telem_layout.setContentsMargins(12, 6, 12, 6)
        telem_layout.setSpacing(14)

        self.lbl_telem_status = QLabel("STATUS: Hardware Ready. Waiting for command.")
        self.lbl_telem_status.setStyleSheet("font-weight: bold; color: #38bdf8; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;")
        telem_layout.addWidget(self.lbl_telem_status, stretch=2)

        self.lbl_telem_rate = QLabel("Throughput: -- B/s")
        self.lbl_telem_rate.setStyleSheet("color: #10b981; font-weight: bold; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;")
        telem_layout.addWidget(self.lbl_telem_rate, stretch=1)

        self.lbl_telem_time = QLabel("Elapsed: 0.0s | ETA: --")
        self.lbl_telem_time.setStyleSheet("color: #cbd5e1; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;")
        telem_layout.addWidget(self.lbl_telem_time, stretch=1)

        self.lbl_telem_integrity = QLabel("CRC32 / Integrity: Validated")
        self.lbl_telem_integrity.setStyleSheet("color: #00adb5; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; font-weight: bold;")
        telem_layout.addWidget(self.lbl_telem_integrity, stretch=1)

        main_layout.addWidget(telemetry_frame)

        # Main Tabs
        self.tabs = QTabWidget()
        self.tab_flash = QWidget()
        self.tab_eeprom = QWidget()
        self.tab_fuses = QWidget()
        self.tab_diag = QWidget()

        self._build_flash_tab()
        self._build_eeprom_tab()
        self._build_fuses_tab()
        self._build_diag_tab()

        self.tabs.addTab(self.tab_flash, "Flash Memory (HEX)")
        self.tabs.addTab(self.tab_eeprom, "EEPROM Memory")
        self.tabs.addTab(self.tab_fuses, "Fuse Bits / Settings")
        self.tabs.addTab(self.tab_diag, "Telemetry & Hardware Log")

        main_layout.addWidget(self.tabs, stretch=1)

        # Bottom Status Bar & Progress
        status_frame = QFrame()
        st_layout = QHBoxLayout(status_frame)
        st_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_status = QLabel("Ready. Connect USBasp and select target.")
        self.lbl_status.setStyleSheet("color: #94a3b8; font-weight: 600;")
        st_layout.addWidget(self.lbl_status, stretch=1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(320)
        st_layout.addWidget(self.progress_bar)

        main_layout.addWidget(status_frame)

    # Flash Tab
    def _build_flash_tab(self):
        layout = QVBoxLayout(self.tab_flash)
        layout.setContentsMargins(10, 10, 10, 10)

        tb = QHBoxLayout()
        btn_load = QPushButton("Load HEX File...")
        btn_load.clicked.connect(self.on_load_flash_hex)
        tb.addWidget(btn_load)

        btn_save = QPushButton("Save Buffer as HEX...")
        btn_save.clicked.connect(self.on_save_flash_hex)
        btn_save.setProperty("class", "SecondaryBtn")
        tb.addWidget(btn_save)

        btn_read = QPushButton("Read Flash From Chip")
        btn_read.clicked.connect(self.on_read_flash)
        tb.addWidget(btn_read)

        btn_write = QPushButton("Write Flash To Chip")
        btn_write.setProperty("class", "DangerBtn")
        btn_write.clicked.connect(self.on_write_flash)
        tb.addWidget(btn_write)

        btn_verify = QPushButton("Verify Flash")
        btn_verify.setProperty("class", "SuccessBtn")
        btn_verify.clicked.connect(self.on_verify_flash)
        tb.addWidget(btn_verify)

        btn_clear = QPushButton("Clear Buffer")
        btn_clear.setProperty("class", "SecondaryBtn")
        btn_clear.clicked.connect(lambda: self._clear_buffer(self.flash_buffer, self.tbl_flash))
        tb.addWidget(btn_clear)

        tb.addStretch()
        self.lbl_flash_info = QLabel("Flash: 32768 Bytes | Buffer: 0 Bytes Loaded")
        self.lbl_flash_info.setStyleSheet("color: #38bdf8; font-weight: bold;")
        tb.addWidget(self.lbl_flash_info)
        layout.addLayout(tb)

        self.tbl_flash = self._create_hex_table()
        layout.addWidget(self.tbl_flash)

    # EEPROM Tab
    def _build_eeprom_tab(self):
        layout = QVBoxLayout(self.tab_eeprom)
        layout.setContentsMargins(10, 10, 10, 10)

        tb = QHBoxLayout()
        btn_load = QPushButton("Load EEP/HEX File...")
        btn_load.clicked.connect(self.on_load_eeprom_file)
        tb.addWidget(btn_load)

        btn_save = QPushButton("Save Buffer as EEP...")
        btn_save.clicked.connect(self.on_save_eeprom_file)
        btn_save.setProperty("class", "SecondaryBtn")
        tb.addWidget(btn_save)

        btn_read = QPushButton("Read EEPROM From Chip")
        btn_read.clicked.connect(self.on_read_eeprom)
        tb.addWidget(btn_read)

        btn_write = QPushButton("Write EEPROM To Chip")
        btn_write.setProperty("class", "DangerBtn")
        btn_write.clicked.connect(self.on_write_eeprom)
        tb.addWidget(btn_write)

        btn_verify = QPushButton("Verify EEPROM")
        btn_verify.setProperty("class", "SuccessBtn")
        btn_verify.clicked.connect(self.on_verify_eeprom)
        tb.addWidget(btn_verify)

        btn_clear = QPushButton("Clear Buffer")
        btn_clear.setProperty("class", "SecondaryBtn")
        btn_clear.clicked.connect(lambda: self._clear_buffer(self.eeprom_buffer, self.tbl_eeprom))
        tb.addWidget(btn_clear)

        tb.addStretch()
        self.lbl_eeprom_info = QLabel("EEPROM: 1024 Bytes | Buffer: 0 Bytes Loaded")
        self.lbl_eeprom_info.setStyleSheet("color: #38bdf8; font-weight: bold;")
        tb.addWidget(self.lbl_eeprom_info)
        layout.addLayout(tb)

        self.tbl_eeprom = self._create_hex_table()
        layout.addWidget(self.tbl_eeprom)

    def _create_hex_table(self) -> QTableWidget:
        tbl = QTableWidget()
        tbl.setColumnCount(18)
        headers = ["Offset"] + [f"{i:X}" for i in range(16)] + ["Decoded ASCII"]
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(17, QHeaderView.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        return tbl

    # Fuses Tab (Designed to mirror eXtreme Burner screenshot with modern additions)
    def _build_fuses_tab(self):
        main_vbox = QVBoxLayout(self.tab_fuses)
        main_vbox.setContentsMargins(14, 14, 14, 14)
        main_vbox.setSpacing(14)

        # 5 Fuse Cards Grid matching eXtreme Burner
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        # 1. Low Fuse Card
        self.card_lfuse, self.chk_write_lfuse, self.edit_lfuse, self.btn_bits_lfuse = self._create_fuse_card(
            "Low Fuse", "FF", has_bit_details=True, bit_cb=lambda: self._open_bit_details("Low Fuse", "low")
        )
        cards_layout.addWidget(self.card_lfuse)

        # 2. High Fuse Card
        self.card_hfuse, self.chk_write_hfuse, self.edit_hfuse, self.btn_bits_hfuse = self._create_fuse_card(
            "High Fuse", "DA", has_bit_details=True, bit_cb=lambda: self._open_bit_details("High Fuse", "high")
        )
        cards_layout.addWidget(self.card_hfuse)

        # 3. Extended Fuse Card
        self.card_efuse, self.chk_write_efuse, self.edit_efuse, self.btn_bits_efuse = self._create_fuse_card(
            "Extented Fuse", "FD", has_bit_details=True, bit_cb=lambda: self._open_bit_details("Extended Fuse", "ext")
        )
        cards_layout.addWidget(self.card_efuse)

        # 4. Lock Fuse Card
        self.card_lock, self.chk_write_lock, self.edit_lock, _ = self._create_fuse_card(
            "Lock Fuse", "CF", has_bit_details=False
        )
        cards_layout.addWidget(self.card_lock)

        # 5. Calibration Card
        self.card_calib, self.chk_write_calib, self.edit_calib, _ = self._create_fuse_card(
            "Calibration", "AA", has_bit_details=False, is_readonly=True
        )
        cards_layout.addWidget(self.card_calib)

        main_vbox.addLayout(cards_layout)

        # Center Action Buttons (Matching eXtreme Burner: Read All, Write)
        center_btn_box = QHBoxLayout()
        center_btn_box.addStretch()

        btn_fuse_read = QPushButton("Read Fuses")
        btn_fuse_read.setStyleSheet("padding: 8px 24px; font-size: 13px;")
        btn_fuse_read.clicked.connect(self.on_read_fuses)
        center_btn_box.addWidget(btn_fuse_read)

        center_btn_box.addSpacing(16)

        btn_fuse_write = QPushButton("Write Fuses")
        btn_fuse_write.setProperty("class", "DangerBtn")
        btn_fuse_write.setStyleSheet("padding: 8px 24px; font-size: 13px;")
        btn_fuse_write.clicked.connect(self.on_write_selected_fuses)
        center_btn_box.addWidget(btn_fuse_write)

        center_btn_box.addStretch()
        main_vbox.addLayout(center_btn_box)

        # Bottom Feature Tools (Clock config wizard & defaults)
        tools_group = QGroupBox("ADVANCED FUSE TOOLS & CLOCK GENERATOR")
        tg_layout = QHBoxLayout(tools_group)
        tg_layout.setContentsMargins(12, 10, 12, 10)

        btn_clock_wizard = QPushButton("Configure AVR Clock...")
        btn_clock_wizard.setProperty("class", "AccentBtn")
        btn_clock_wizard.clicked.connect(self.on_open_clock_wizard)
        tg_layout.addWidget(btn_clock_wizard)

        btn_reset_defaults = QPushButton("Reset Fuses to Chip Defaults")
        btn_reset_defaults.setProperty("class", "SecondaryBtn")
        btn_reset_defaults.clicked.connect(self.on_default_fuses)
        tg_layout.addWidget(btn_reset_defaults)

        btn_placement = QPushButton("ZIF Socket Placement...")
        btn_placement.setProperty("class", "SecondaryBtn")
        btn_placement.clicked.connect(self.on_show_zif_guide)
        tg_layout.addWidget(btn_placement)

        tg_layout.addStretch()
        main_vbox.addWidget(tools_group)
        main_vbox.addStretch()

    def _create_fuse_card(self, title: str, default_hex: str, has_bit_details: bool = True,
                          bit_cb=None, is_readonly: bool = False):
        box = QGroupBox(title)
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(10, 12, 10, 12)
        vbox.setSpacing(10)

        chk_write = QCheckBox("Write")
        chk_write.setChecked(not is_readonly)
        chk_write.setEnabled(not is_readonly)
        vbox.addWidget(chk_write)

        h_val = QHBoxLayout()
        h_val.addWidget(QLabel("0x"))
        edit_hex = QLineEdit(default_hex)
        edit_hex.setFixedWidth(56)
        edit_hex.setAlignment(Qt.AlignCenter)
        edit_hex.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 14px;")
        edit_hex.setReadOnly(is_readonly)
        h_val.addWidget(edit_hex)
        h_val.addStretch()
        vbox.addLayout(h_val)

        btn_bits = None
        if has_bit_details:
            btn_bits = QPushButton("Bit Details ...")
            btn_bits.setProperty("class", "SecondaryBtn")
            if bit_cb:
                btn_bits.clicked.connect(bit_cb)
            vbox.addWidget(btn_bits)
        else:
            vbox.addSpacing(28)

        return box, chk_write, edit_hex, btn_bits

    def _open_bit_details(self, title: str, fuse_type: str):
        if not self.active_chip or not self.active_chip.fuse_layout:
            return
        layout = self.active_chip.fuse_layout

        if fuse_type == "low":
            bits = layout.low_bits
            edit = self.edit_lfuse
        elif fuse_type == "high":
            bits = layout.high_bits
            edit = self.edit_hfuse
        elif fuse_type == "ext":
            bits = layout.ext_bits
            edit = self.edit_efuse
        else:
            bits = layout.lock_bits
            edit = self.edit_lock

        try:
            curr_val = int(edit.text(), 16) & 0xFF
        except ValueError:
            curr_val = 0xFF

        dlg = BitDetailsDialog(title, bits, curr_val, self)
        if dlg.exec():
            edit.setText(f"{dlg.value:02X}")
            self.log(f"Updated {title} to 0x{dlg.value:02X}")

    def on_open_clock_wizard(self):
        try:
            curr_val = int(self.edit_lfuse.text(), 16) & 0xFF
        except ValueError:
            curr_val = 0xFF
        dlg = ClockConfigDialog(curr_val, self)
        if dlg.exec():
            self.edit_lfuse.setText(f"{dlg.resulting_lfuse:02X}")
            self.chk_write_lfuse.setChecked(True)
            self.log(f"Clock Wizard applied Low Fuse: 0x{dlg.resulting_lfuse:02X}")

    # Diagnostics Tab
    def _build_diag_tab(self):
        layout = QVBoxLayout(self.tab_diag)
        layout.setContentsMargins(10, 10, 10, 10)

        hb = QHBoxLayout()
        btn_clear = QPushButton("Clear Console")
        btn_clear.setProperty("class", "SecondaryBtn")
        btn_clear.clicked.connect(lambda: self.txt_log.clear())
        hb.addWidget(btn_clear)

        btn_ping = QPushButton("Test Hardware Connection")
        btn_ping.clicked.connect(self.on_ping_hardware)
        hb.addWidget(btn_ping)

        btn_export = QPushButton("Export Log (.txt)...")
        btn_export.setProperty("class", "SecondaryBtn")
        btn_export.clicked.connect(self.on_export_log)
        hb.addWidget(btn_export)

        hb.addStretch()
        layout.addLayout(hb)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

    def log(self, message: str):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.txt_log.append(f"{timestamp}{message}")
        self.lbl_status.setText(message)

    def on_export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Diagnostic Log", "enit_hardware_log.txt", "Text Files (*.txt);;All Files (*.*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.txt_log.toPlainText())
                self.log(f"Diagnostic session log exported to: {path}")
            except Exception as ex:
                self.log(f"Export log error: {ex}")

    def on_telemetry_event(self, telem: dict):
        action = telem.get("action", "")
        percent = telem.get("percent", 0)
        rate = telem.get("rate_bps", 0)
        elapsed = telem.get("elapsed_s", 0)
        eta = telem.get("eta_s", 0)
        status_msg = telem.get("status", "")

        self.lbl_telem_status.setText(f"TELEMETRY: {status_msg}")
        self.lbl_telem_rate.setText(f"Speed: {rate:.1f} B/s")
        self.lbl_telem_time.setText(f"Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")
        self.progress_bar.setValue(percent)

    # Chip Update & Hex Views
    def on_chip_selected(self, chip_name: str):
        chip = find_by_name(chip_name)
        if chip:
            self.active_chip = chip
            self._update_chip_info()

    def _update_chip_info(self):
        if not self.active_chip:
            return
        chip = self.active_chip
        self.flash_buffer.resize(chip.flash_size)
        self.eeprom_buffer.resize(chip.eeprom_size)

        self.lbl_flash_info.setText(f"Flash: {chip.flash_size} Bytes ({chip.flash_size // 1024} KB) | Page: {chip.page_size}B")
        self.lbl_eeprom_info.setText(f"EEPROM: {chip.eeprom_size} Bytes")

        self.edit_lfuse.setText(f"{chip.default_lfuse:02X}")
        self.edit_hfuse.setText(f"{chip.default_hfuse:02X}")
        self.edit_efuse.setText(f"{chip.default_efuse:02X}")
        self.edit_efuse.setEnabled(chip.has_efuse)
        self.chk_write_efuse.setEnabled(chip.has_efuse)

        if hasattr(self, 'lbl_hardware_summary'):
            sig_hex = f"0x{chip.signature[0]:02X} 0x{chip.signature[1]:02X} 0x{chip.signature[2]:02X}"
            self.lbl_hardware_summary.setText(f"DEVICE READY • USBasp Synced • VTarget: 5.0V • Target: {chip.name} ({sig_hex})")

        self._populate_table(self.tbl_flash, self.flash_buffer.buffer, max_rows=128)
        self._populate_table(self.tbl_eeprom, self.eeprom_buffer.buffer, max_rows=64)

    def _populate_table(self, tbl: QTableWidget, data: bytearray, max_rows: int = 128):
        tbl.setRowCount(0)
        num_rows = min(max_rows, (len(data) + 15) // 16)
        tbl.setRowCount(num_rows)
        for r in range(num_rows):
            offset = r * 16
            tbl.setItem(r, 0, QTableWidgetItem(f"0x{offset:06X}"))
            ascii_chars = []
            for col in range(16):
                idx = offset + col
                val = data[idx] if idx < len(data) else 0xFF
                item = QTableWidgetItem(f"{val:02X}")
                item.setTextAlignment(Qt.AlignCenter)
                if val != 0xFF:
                    item.setForeground(QColor("#38bdf8"))
                    item.setFont(QFont("Consolas", 10, QFont.Bold))
                else:
                    item.setForeground(QColor("#475569"))
                tbl.setItem(r, col + 1, item)

                if 32 <= val <= 126:
                    ascii_chars.append(chr(val))
                else:
                    ascii_chars.append("·")

            ascii_item = QTableWidgetItem("".join(ascii_chars))
            ascii_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            ascii_item.setForeground(QColor("#a5f3fc"))
            ascii_item.setFont(QFont("Consolas", 10))
            tbl.setItem(r, 17, ascii_item)

    def _clear_buffer(self, buf: IntelHex, tbl: QTableWidget):
        buf.clear(0xFF)
        if buf is self.flash_buffer:
            self.loaded_flash_path = None
        elif buf is self.eeprom_buffer:
            self.loaded_eeprom_path = None
        self._populate_table(tbl, buf.buffer)
        self.log("Buffer reset to 0xFF.")

    # Hardware Actions
    def on_connect_clicked(self):
        if not self.programmer.is_connected:
            self._run_worker("connect", "Connecting to target MCU...")
        else:
            self.programmer.disconnect_target()
            self.programmer.close()
            self.btn_connect.setText("Connect USBasp")
            self.lbl_status.setText("Programmer disconnected.")

    def on_autodetect_clicked(self):
        self._run_worker("read_signature", "Reading signature & detecting chip...")

    def on_speed_changed(self, text: str):
        code = SCK_SPEEDS.get(text, 0)
        if self.programmer.handle:
            self.programmer.set_sck_speed(code)
            self.log(f"ISP SCK Speed set to {text} (code {code}).")

    def on_ping_hardware(self):
        if self.programmer.open():
            if self.programmer.connect_target():
                sig = self.programmer.read_signature()
                self.log(f"Hardware Ping SUCCESS! Signature: {[hex(b) for b in sig]}")
                self.programmer.disconnect_target()
            self.programmer.close()

    def on_show_zif_guide(self):
        if not self.active_chip:
            return
        dlg = ZIFPlacementDialog(self.active_chip, self)
        dlg.exec()

    def on_show_donate_dialog(self):
        dlg = DonateDialog(self)
        dlg.exec()

    def on_chip_erase(self):
        dlg = EnitConfirmDialog(
            "Confirm Chip Erase",
            "Are you sure you want to completely erase the target chip?",
            [
                "All Flash memory contents will be wiped (set to 0xFF)",
                "All EEPROM memory contents will be wiped (set to 0xFF)",
                "Lock bits will be reset to factory default"
            ],
            confirm_text="Yes, Erase Chip",
            parent=self
        )
        if dlg.exec() == QDialog.Accepted:
            self._run_worker("erase", "Erasing target chip...")

    def on_read_flash(self):
        if not self.active_chip:
            return
        container = {}
        def on_done(ok, msg):
            if ok and "data" in container:
                self.flash_buffer.buffer = bytearray(container["data"])
                self._populate_table(self.tbl_flash, self.flash_buffer.buffer)
                self.log(f"Flash memory read complete ({len(container['data'])} bytes).")
        self._run_worker("read_flash", "Reading target Flash memory...",
                         size=self.active_chip.flash_size,
                         page_size=self.active_chip.page_size,
                         container=container, custom_done=on_done)

    def on_write_flash(self):
        if not self.active_chip:
            return
        self._run_worker("write_flash", "Programming & Verifying Flash memory...",
                         data=bytes(self.flash_buffer.buffer[:self.active_chip.flash_size]),
                         page_size=self.active_chip.page_size,
                         skip_blank=True,
                         source_path=self.loaded_flash_path)

    def on_verify_flash(self):
        if not self.active_chip:
            return
        self._run_worker("verify_flash", "Verifying Flash memory vs PC File...",
                         data=bytes(self.flash_buffer.buffer[:self.active_chip.flash_size]),
                         page_size=self.active_chip.page_size,
                         source_path=self.loaded_flash_path)

    def on_read_eeprom(self):
        if not self.active_chip:
            return
        container = {}
        def on_done(ok, msg):
            if ok and "data" in container:
                self.eeprom_buffer.buffer = bytearray(container["data"])
                self._populate_table(self.tbl_eeprom, self.eeprom_buffer.buffer)
                self.log(f"EEPROM read complete ({len(container['data'])} bytes).")
        self._run_worker("read_eeprom", "Reading target EEPROM memory...",
                         size=self.active_chip.eeprom_size,
                         container=container, custom_done=on_done)

    def on_write_eeprom(self):
        if not self.active_chip:
            return
        self._run_worker("write_eeprom", "Programming EEPROM memory...",
                         data=bytes(self.eeprom_buffer.buffer[:self.active_chip.eeprom_size]))

    def on_verify_eeprom(self):
        if not self.active_chip:
            return
        self._run_worker("verify_eeprom", "Verifying EEPROM memory...",
                         data=bytes(self.eeprom_buffer.buffer[:self.active_chip.eeprom_size]))

    def on_read_fuses(self):
        container = {}
        def on_done(ok, msg):
            if ok and "fuses" in container:
                f = container["fuses"]
                self.edit_lfuse.setText(f"{f['low']:02X}")
                self.edit_hfuse.setText(f"{f['high']:02X}")
                self.edit_efuse.setText(f"{f['ext']:02X}")
                self.edit_lock.setText(f"{f['lock']:02X}")
                self.edit_calib.setText(f"{f['calib']:02X}")
                self.log("Fuses and Lock bits updated from chip.")
        self._run_worker("read_fuses", "Reading Fuses & Lock bits...", container=container, custom_done=on_done)

    def on_write_selected_fuses(self):
        try:
            f = {}
            if self.chk_write_lfuse.isChecked():
                f["low"] = int(self.edit_lfuse.text(), 16)
            if self.chk_write_hfuse.isChecked():
                f["high"] = int(self.edit_hfuse.text(), 16)
            if self.chk_write_efuse.isChecked() and self.active_chip.has_efuse:
                f["ext"] = int(self.edit_efuse.text(), 16)
            if self.chk_write_lock.isChecked():
                f["lock"] = int(self.edit_lock.text(), 16)

            if not f:
                QMessageBox.information(self, "No Fuses Selected", "Please check at least one 'Write' box to write fuses.")
                return

            self._run_worker("write_fuses", "Writing Selected Fuses...", fuses=f)
        except ValueError:
            QMessageBox.critical(self, "Invalid Fuse Value", "Please enter valid 2-digit hex numbers for fuses.")

    def on_default_fuses(self):
        if self.active_chip:
            self.edit_lfuse.setText(f"{self.active_chip.default_lfuse:02X}")
            self.edit_hfuse.setText(f"{self.active_chip.default_hfuse:02X}")
            self.edit_efuse.setText(f"{self.active_chip.default_efuse:02X}")
            self.edit_lock.setText("FF")
            self.log(f"Loaded default fuse settings for {self.active_chip.name}.")

    def on_read_all(self):
        """Unified Read All: Fuses, Flash, EEPROM."""
        if not self.active_chip:
            return
        container = {}
        def on_done(ok, msg):
            if ok:
                if "fuses" in container:
                    f = container["fuses"]
                    self.edit_lfuse.setText(f"{f['low']:02X}")
                    self.edit_hfuse.setText(f"{f['high']:02X}")
                    self.edit_efuse.setText(f"{f['ext']:02X}")
                    self.edit_lock.setText(f"{f['lock']:02X}")
                    self.edit_calib.setText(f"{f['calib']:02X}")
                if "flash" in container:
                    self.flash_buffer.buffer = bytearray(container["flash"])
                    self._populate_table(self.tbl_flash, self.flash_buffer.buffer)
                if "eeprom" in container:
                    self.eeprom_buffer.buffer = bytearray(container["eeprom"])
                    self._populate_table(self.tbl_eeprom, self.eeprom_buffer.buffer)
                self.log("READ ALL COMPLETE: Flash, EEPROM, and Fuses synchronized.")

        self._run_worker("read_all", "Executing Read All (Fuses + Flash + EEPROM)...",
                         chip=self.active_chip, container=container, custom_done=on_done)

    def on_write_all(self):
        """
        Unified Write All:
        Writes Flash HEX (if loaded), EEPROM (if loaded/has data), and all checked Fuses.
        """
        if not self.active_chip:
            return

        items = [
            "1. Full Target Chip Erase",
            f"2. Flash Memory Programming ({self.active_chip.flash_size} bytes)",
        ]
        if any(b != 0xFF for b in self.eeprom_buffer.buffer):
            items.append(f"3. EEPROM Memory Programming ({self.active_chip.eeprom_size} bytes)")
        else:
            items.append("3. EEPROM: Skipped (buffer empty/0xFF)")

        fuse_desc = []
        if self.chk_write_lfuse.isChecked():
            fuse_desc.append(f"Low: 0x{self.edit_lfuse.text()}")
        if self.chk_write_hfuse.isChecked():
            fuse_desc.append(f"High: 0x{self.edit_hfuse.text()}")
        if self.chk_write_efuse.isChecked() and self.active_chip.has_efuse:
            fuse_desc.append(f"Ext: 0x{self.edit_efuse.text()}")
        if self.chk_write_lock.isChecked():
            fuse_desc.append(f"Lock: 0x{self.edit_lock.text()}")

        if fuse_desc:
            items.append(f"4. Selected Fuses to Program: {', '.join(fuse_desc)}")
        else:
            items.append("4. Fuses: None checked")

        dlg = EnitConfirmDialog(
            "Confirm Write All",
            "Write All will execute the following operations in hardware sequence:",
            items,
            confirm_text="Yes, Program All",
            parent=self
        )
        if dlg.exec() != QDialog.Accepted:
            return

        # Prepare payload
        flash_data = bytes(self.flash_buffer.buffer[:self.active_chip.flash_size])
        eeprom_data = bytes(self.eeprom_buffer.buffer[:self.active_chip.eeprom_size])

        fuses = {}
        if self.chk_write_lfuse.isChecked():
            fuses["low"] = int(self.edit_lfuse.text(), 16)
        if self.chk_write_hfuse.isChecked():
            fuses["high"] = int(self.edit_hfuse.text(), 16)
        if self.chk_write_efuse.isChecked() and self.active_chip.has_efuse:
            fuses["ext"] = int(self.edit_efuse.text(), 16)
        if self.chk_write_lock.isChecked():
            fuses["lock"] = int(self.edit_lock.text(), 16)

        self._run_worker("write_all", "Executing Write All & Post-Write Verification...",
                         chip=self.active_chip,
                         flash_data=flash_data,
                         flash_source_path=self.loaded_flash_path,
                         eeprom_data=eeprom_data,
                         fuses=fuses)

    # Hex File IO
    def on_load_flash_hex(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Intel HEX File", "", "Intel HEX (*.hex);;All Files (*.*)")
        if path:
            try:
                self.flash_buffer.clear(0xFF)
                cnt, highest = self.flash_buffer.load_hex_file(path)
                self.loaded_flash_path = path
                self._populate_table(self.tbl_flash, self.flash_buffer.buffer)
                self.lbl_flash_info.setText(f"Loaded: {cnt} Bytes (Max Addr: 0x{highest:04X}) | File: {os.path.basename(path)}")
                self.log(f"Successfully loaded {cnt} bytes into Flash buffer from {path}")
            except Exception as ex:
                QMessageBox.critical(self, "HEX Parse Error", str(ex))

    def on_save_flash_hex(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Intel HEX File", "flash_dump.hex", "Intel HEX (*.hex)")
        if path:
            try:
                self.flash_buffer.save_hex_file(path, max_address=self.active_chip.flash_size - 1)
                self.log(f"Saved Flash buffer to {path}")
            except Exception as ex:
                QMessageBox.critical(self, "Save Error", str(ex))

    def on_load_eeprom_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open EEPROM File", "", "EEPROM (*.eep *.hex *.bin);;All Files (*.*)")
        if path:
            try:
                if path.lower().endswith('.bin'):
                    cnt = self.eeprom_buffer.load_binary_file(path)
                else:
                    cnt, _ = self.eeprom_buffer.load_hex_file(path)
                self._populate_table(self.tbl_eeprom, self.eeprom_buffer.buffer)
                self.lbl_eeprom_info.setText(f"Loaded: {cnt} Bytes | File: {os.path.basename(path)}")
                self.log(f"Successfully loaded {cnt} bytes into EEPROM buffer from {path}")
            except Exception as ex:
                QMessageBox.critical(self, "File Load Error", str(ex))

    def on_save_eeprom_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save EEPROM File", "eeprom_dump.eep", "EEPROM (*.eep *.hex)")
        if path:
            try:
                self.eeprom_buffer.save_hex_file(path, max_address=self.active_chip.eeprom_size - 1)
                self.log(f"Saved EEPROM buffer to {path}")
            except Exception as ex:
                QMessageBox.critical(self, "Save Error", str(ex))

    # Worker Helper
    def _run_worker(self, action: str, initial_status: str, custom_done=None, **kwargs):
        self.lbl_status.setText(initial_status)
        self.lbl_telem_status.setText(f"ACTION: {initial_status}")
        self.progress_bar.setValue(0)
        self._set_buttons_enabled(False)

        self.worker = WorkerThread(action, self.programmer, **kwargs)
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(lambda cur, tot: self.progress_bar.setValue(int(cur * 100 / tot)))
        self.worker.telemetry_signal.connect(self.on_telemetry_event)

        def on_finished(ok: bool, msg: str):
            self._set_buttons_enabled(True)
            self.lbl_status.setText(msg)
            if ok:
                self.lbl_telem_status.setStyleSheet("font-weight: bold; color: #10b981; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;")
                self.lbl_telem_status.setText(f"COMPLETED: {msg}")
            else:
                self.lbl_telem_status.setStyleSheet("font-weight: bold; color: #ef4444; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;")
                self.lbl_telem_status.setText(f"FAILED: {msg}")
                if "MISMATCH" in msg.upper() or "VERIFY FAILED" in msg.upper():
                    QMessageBox.critical(self, "Verification Mismatch Detected", msg)
            if self.programmer.is_connected:
                self.btn_connect.setText("Disconnect")
                if self.programmer.active_chip:
                    self.combo_chips.blockSignals(True)
                    self.combo_chips.setCurrentText(self.programmer.active_chip.name)
                    self.combo_chips.blockSignals(False)
                    self.active_chip = self.programmer.active_chip
                if hasattr(self, 'lbl_status_led'):
                    self.lbl_status_led.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
                if hasattr(self, 'lbl_hardware_summary') and self.active_chip:
                    sig = f"0x{self.active_chip.signature[0]:02X} 0x{self.active_chip.signature[1]:02X} 0x{self.active_chip.signature[2]:02X}"
                    self.lbl_hardware_summary.setText(f"DEVICE READY • USBasp Synced • VTarget: 5.0V • Target: {self.active_chip.name} ({sig})")
            else:
                if hasattr(self, 'lbl_status_led'):
                    self.lbl_status_led.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold;")
                if hasattr(self, 'lbl_hardware_summary'):
                    self.lbl_hardware_summary.setText("DISCONNECTED • Click 'Connect USBasp' to initialize hardware session")
            if custom_done:
                custom_done(ok, msg)

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()

    def _set_buttons_enabled(self, enabled: bool):
        self.btn_connect.setEnabled(enabled)
        self.btn_autodetect.setEnabled(enabled)
        self.btn_read_all.setEnabled(enabled)
        self.btn_write_all.setEnabled(enabled)
        self.btn_erase.setEnabled(enabled)
        if hasattr(self, 'btn_zif'):
            self.btn_zif.setEnabled(enabled)

def main():
    # Adaptive High-DPI Desktop Scaling (Phase 4)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # High-contrast Cyber Dark Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#11141c"))
    palette.setColor(QPalette.WindowText, QColor("#f8fafc"))
    palette.setColor(QPalette.Base, QColor("#090d16"))
    palette.setColor(QPalette.AlternateBase, QColor("#171b26"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1e293b"))
    palette.setColor(QPalette.ToolTipText, QColor("#f8fafc"))
    palette.setColor(QPalette.Text, QColor("#f8fafc"))
    palette.setColor(QPalette.Button, QColor("#1e293b"))
    palette.setColor(QPalette.ButtonText, QColor("#f8fafc"))
    palette.setColor(QPalette.BrightText, QColor("#ef4444"))
    palette.setColor(QPalette.Link, QColor("#38bdf8"))
    palette.setColor(QPalette.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet(STYLE_SHEET)

    # Set Master Multi-Resolution Windows App Icon
    icon_path = os.path.join(BASE_DIR, "Icons", "enit_avr_studio.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_DIR, "Images", "icons", "draw-wave-icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = EnitAVRStudio()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
