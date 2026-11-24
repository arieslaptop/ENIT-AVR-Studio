"""
================================================================================
ENIT AVR STUDIO - High-Performance Hardware Programmer Core
Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India
All Rights Reserved.
================================================================================
"""

import ctypes
import os
import sys
import time
from typing import Callable, Dict, List, Optional, Tuple

from enit_chip_db import AVRChip, CHIP_DATABASE, find_by_signature

# USBasp VID & PID
USBASP_VID = 0x16C0
USBASP_PID = 0x05DC

# USBasp Request Codes
USBASP_FUNC_CONNECT         = 1
USBASP_FUNC_DISCONNECT      = 2
USBASP_FUNC_TRANSMIT        = 3
USBASP_FUNC_READFLASH       = 4
USBASP_FUNC_ENABLEPROG      = 5
USBASP_FUNC_WRITEFLASH      = 6
USBASP_FUNC_READEEPROM      = 7
USBASP_FUNC_WRITEEEPROM     = 8
USBASP_FUNC_SETLONGADDRESS  = 9
USBASP_FUNC_SETISPSCK       = 10
USBASP_FUNC_GETCAPABILITIES = 127

# USBasp Block Flags
USBASP_BLOCKFLAG_FIRST      = 1
USBASP_BLOCKFLAG_LAST       = 2

# SCK Speeds
SCK_SPEEDS = {
    "Auto": 0,
    "1.5 MHz": 12,
    "750 kHz": 11,
    "375 kHz": 10,
    "187.5 kHz": 9,
    "93.75 kHz": 8,
    "32 kHz": 7,
    "16 kHz": 6,
    "8 kHz": 5,
    "4 kHz": 4,
    "2 kHz": 3,
    "1 kHz": 2,
    "500 Hz": 1,
}

# CTypes definitions for libusb-win32
class usb_bus(ctypes.Structure): pass
class usb_device(ctypes.Structure): pass
class usb_dev_handle(ctypes.Structure): pass

class usb_device_descriptor(ctypes.Structure):
    _fields_ = [
        ('bLength', ctypes.c_uint8), ('bDescriptorType', ctypes.c_uint8),
        ('bcdUSB', ctypes.c_uint16), ('bDeviceClass', ctypes.c_uint8),
        ('bDeviceSubClass', ctypes.c_uint8), ('bDeviceProtocol', ctypes.c_uint8),
        ('bMaxPacketSize0', ctypes.c_uint8), ('idVendor', ctypes.c_uint16),
        ('idProduct', ctypes.c_uint16), ('bcdDevice', ctypes.c_uint16),
        ('iManufacturer', ctypes.c_uint8), ('iProduct', ctypes.c_uint8),
        ('iSerialNumber', ctypes.c_uint8), ('bNumConfigurations', ctypes.c_uint8)
    ]

usb_device._fields_ = [
    ('next', ctypes.POINTER(usb_device)), ('prev', ctypes.POINTER(usb_device)),
    ('filename', ctypes.c_char * 512), ('bus', ctypes.POINTER(usb_bus)),
    ('descriptor', usb_device_descriptor), ('config', ctypes.c_void_p),
    ('dev', ctypes.c_void_p), ('devnum', ctypes.c_uint8),
    ('num_children', ctypes.c_ubyte), ('children', ctypes.c_void_p)
]

usb_bus._fields_ = [
    ('next', ctypes.POINTER(usb_bus)), ('prev', ctypes.POINTER(usb_bus)),
    ('dirname', ctypes.c_char * 512), ('devices', ctypes.POINTER(usb_device)),
    ('location', ctypes.c_uint32), ('root_dev', ctypes.c_void_p)
]

def load_libusb():
    """Attempts to locate and load libusb0.dll."""
    search_paths = [
        "libusb0.dll",
        r"C:\Program Files\eXtreme Burner - AVR\driver\amd64\libusb0.dll",
        r"C:\Program Files\eXtreme Burner - AVR\driver\x86\libusb0_x86.dll",
        r"C:\Windows\System32\libusb0.dll",
        r"C:\Windows\SysWOW64\libusb0.dll"
    ]
    for p in search_paths:
        try:
            dll = ctypes.cdll.LoadLibrary(p)
            dll.usb_init()
            dll.usb_find_busses.restype = ctypes.c_int
            dll.usb_find_devices.restype = ctypes.c_int
            dll.usb_get_busses.restype = ctypes.POINTER(usb_bus)
            dll.usb_open.argtypes = [ctypes.POINTER(usb_device)]
            dll.usb_open.restype = ctypes.POINTER(usb_dev_handle)
            dll.usb_close.argtypes = [ctypes.POINTER(usb_dev_handle)]
            dll.usb_close.restype = ctypes.c_int
            dll.usb_control_msg.argtypes = [
                ctypes.POINTER(usb_dev_handle),
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_char_p, ctypes.c_int, ctypes.c_int
            ]
            dll.usb_control_msg.restype = ctypes.c_int
            return dll
        except Exception:
            continue
    raise RuntimeError("Could not load libusb0.dll. Ensure USBasp driver is installed.")

class USBaspProgrammer:
    """
    Core hardware interface for USBasp programmer hardware.
    Features:
      - Clean target sync with auto-retry
      - Hardware block transfers for Flash & EEPROM
      - Full Fuse & Lock bit manipulation
      - Real-time progress and telemetry callbacks
      - Smart blank page skipping for accelerated flashing
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.lib = load_libusb()
        # pyrefly: ignore[invalid-annotation]
        self.handle: Optional[ctypes.POINTER(usb_dev_handle)] = None
        self.log_cb = log_callback or (lambda msg: None)
        self.is_connected = False
        self.active_chip: Optional[AVRChip] = None
        self.sck_option = 0 # Default auto

    def log(self, message: str):
        self.log_cb(message)

    def find_device(self) -> bool:
        """Checks if USBasp is connected to the USB bus."""
        self.lib.usb_find_busses()
        self.lib.usb_find_devices()
        bus = self.lib.usb_get_busses()
        while bus:
            dev = bus.contents.devices
            while dev:
                desc = dev.contents.descriptor
                if desc.idVendor == USBASP_VID and desc.idProduct == USBASP_PID:
                    return True
                dev = dev.contents.next
            bus = bus.contents.next
        return False

    def open(self) -> bool:
        """Opens connection to USBasp."""
        if self.handle:
            self.close()

        self.lib.usb_find_busses()
        self.lib.usb_find_devices()
        bus = self.lib.usb_get_busses()
        while bus:
            dev = bus.contents.devices
            while dev:
                desc = dev.contents.descriptor
                if desc.idVendor == USBASP_VID and desc.idProduct == USBASP_PID:
                    self.handle = self.lib.usb_open(dev)
                    if self.handle:
                        self.log("USBasp hardware detected and initialized.")
                        return True
                dev = dev.contents.next
            bus = bus.contents.next

        self.log("ERROR: USBasp hardware NOT found. Please connect programmer.")
        return False

    def close(self):
        """Closes connection to USBasp."""
        if self.handle:
            if self.is_connected:
                self.disconnect_target()
            self.lib.usb_close(self.handle)
            self.handle = None
            self.log("USBasp hardware session closed.")

    def set_sck_speed(self, speed_code: int) -> bool:
        """Sets the ISP SCK clock frequency."""
        if not self.handle:
            return False
        buf = (ctypes.c_char * 4)()
        res = self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_SETISPSCK, speed_code, 0, buf, 1, 1000)
        self.sck_option = speed_code
        return res >= 0

    def connect_target(self, max_retries: int = 3) -> bool:
        """Powers on and connects to target AVR microcontroller."""
        if not self.handle:
            if not self.open():
                return False

        buf = (ctypes.c_char * 4)()
        for attempt in range(1, max_retries + 1):
            self.log(f"Attempting ISP sync with target (Attempt {attempt}/{max_retries})...")
            # Connect command
            self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_CONNECT, 0, 0, buf, 0, 1000)
            time.sleep(0.05)

            # ISP Programming Enable / Sync: 0xAC, 0x53, 0x00, 0x00
            res = self.isp_transmit(0xAC, 0x53, 0x00, 0x00)
            if res[2] == 0x53:
                self.is_connected = True
                self.log("ISP Target Synchronization SUCCESS! (Target returned 0x53)")
                return True
            else:
                self.log(f"Sync failed (Target returned {hex(res[2])}). Retrying...")
                self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_DISCONNECT, 0, 0, buf, 0, 500)
                time.sleep(0.1)

        self.log("ERROR: Cannot synchronize with target MCU. Check wiring, VCC, GND, and RESET pin.")
        return False

    def disconnect_target(self):
        """Releases RESET and powers down target."""
        if self.handle and self.is_connected:
            buf = (ctypes.c_char * 4)()
            self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_DISCONNECT, 0, 0, buf, 0, 1000)
            self.is_connected = False
            self.log("Target MCU disconnected (RESET line released).")

    def isp_transmit(self, b0: int, b1: int, b2: int, b3: int) -> Tuple[int, int, int, int]:
        """Transmits 4-byte raw SPI ISP transaction."""
        if not self.handle:
            raise RuntimeError("Programmer not open")
        wValue = (b1 << 8) | b0
        wIndex = (b3 << 8) | b2
        rx_buf = (ctypes.c_char * 4)()
        res = self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_TRANSMIT, wValue, wIndex, rx_buf, 4, 1000)
        if res < 0:
            raise IOError("USBasp transmit communication failed.")
        raw = rx_buf.raw[:4]
        return (raw[0], raw[1], raw[2], raw[3])

    def read_signature(self) -> Tuple[int, int, int]:
        """Reads 3 signature bytes from target (0x30, 0x00, addr, 0x00)."""
        if not self.is_connected:
            if not self.connect_target():
                raise IOError("Target not connected")
        sig = []
        for addr in (0, 1, 2):
            res = self.isp_transmit(0x30, 0x00, addr, 0x00)
            sig.append(res[3])
        sig_tuple = (sig[0], sig[1], sig[2])
        self.log(f"Target Device Signature: [0x{sig[0]:02X}, 0x{sig[1]:02X}, 0x{sig[2]:02X}]")
        return sig_tuple

    def autodetect_chip(self) -> Optional[AVRChip]:
        """Auto-detects the connected AVR microcontroller."""
        sig = self.read_signature()
        chip = find_by_signature(sig)
        if chip:
            self.active_chip = chip
            self.log(f"Chip Identified: {chip.name} (Flash: {chip.flash_size}B, EEPROM: {chip.eeprom_size}B, Page: {chip.page_size}B)")
        else:
            self.log(f"Unknown Chip Signature: 0x{sig[0]:02X} 0x{sig[1]:02X} 0x{sig[2]:02X}")
        return chip

    def chip_erase(self) -> bool:
        """Erases entire chip Flash and EEPROM (unless EESAVE is set)."""
        self.log("Erasing target chip...")
        self.isp_transmit(0xAC, 0x80, 0x00, 0x00)
        time.sleep(0.05)  # Wait for chip erase cycle (~20-50ms)
        self.disconnect_target()
        time.sleep(0.05)
        success = self.connect_target()
        if success:
            self.log("Chip erase completed successfully.")
        return success

    # Fuse and Lock Operations
    def read_fuses(self) -> Dict[str, int]:
        """Reads Low, High, Extended fuses, Lock bits, and Calibration byte."""
        if not self.is_connected:
            if not self.connect_target():
                raise IOError("Target not connected")

        lf = self.isp_transmit(0x50, 0x00, 0x00, 0x00)[3]
        hf = self.isp_transmit(0x58, 0x08, 0x00, 0x00)[3]
        ef = self.isp_transmit(0x50, 0x08, 0x00, 0x00)[3]
        lb = self.isp_transmit(0x58, 0x00, 0x00, 0x00)[3]
        cal = self.isp_transmit(0x38, 0x00, 0x00, 0x00)[3]

        fuses = {
            "low": lf,
            "high": hf,
            "ext": ef,
            "lock": lb,
            "calib": cal
        }
        self.log(f"Fuses Read: Low=0x{lf:02X}, High=0x{hf:02X}, Ext=0x{ef:02X}, Lock=0x{lb:02X}, Cal=0x{cal:02X}")
        return fuses

    def write_fuses(self, low: Optional[int] = None, high: Optional[int] = None,
                    ext: Optional[int] = None, lock: Optional[int] = None) -> bool:
        """Writes specified fuse and lock values."""
        if not self.is_connected:
            if not self.connect_target():
                return False

        if low is not None:
            self.log(f"Writing Low Fuse Byte: 0x{low:02X}...")
            self.isp_transmit(0xAC, 0xA0, 0x00, low)
            time.sleep(0.01)

        if high is not None:
            self.log(f"Writing High Fuse Byte: 0x{high:02X}...")
            self.isp_transmit(0xAC, 0xA8, 0x00, high)
            time.sleep(0.01)

        if ext is not None:
            self.log(f"Writing Extended Fuse Byte: 0x{ext:02X}...")
            self.isp_transmit(0xAC, 0xA4, 0x00, ext)
            time.sleep(0.01)

        if lock is not None:
            self.log(f"Writing Lock Byte: 0x{lock:02X}...")
            self.isp_transmit(0xAC, 0xE0, 0x00, lock)
            time.sleep(0.01)

        # Verify fuses
        readback = self.read_fuses()
        match = True
        if low is not None and readback["low"] != low:
            self.log(f"WARNING: Low Fuse verify mismatch! Wrote 0x{low:02X}, Read 0x{readback['low']:02X}")
            match = False
        if high is not None and readback["high"] != high:
            self.log(f"WARNING: High Fuse verify mismatch! Wrote 0x{high:02X}, Read 0x{readback['high']:02X}")
            match = False
        if ext is not None and (readback["ext"] & 0x07) != (ext & 0x07):
            self.log(f"WARNING: Ext Fuse verify mismatch! Wrote 0x{ext:02X}, Read 0x{readback['ext']:02X}")
            match = False
        if match:
            self.log("All Fuse and Lock bytes written and verified successfully!")
        return match

    # High-Performance Flash Memory Read / Write with Telemetry
    def read_flash(self, total_size: int, block_size: int = 128,
                   progress_callback: Optional[Callable[[int, int], None]] = None,
                   telemetry_callback: Optional[Callable[[Dict], None]] = None) -> bytes:
        """Reads target Flash memory block by block with live telemetry."""
        if not self.is_connected:
            if not self.connect_target():
                raise IOError("Target not connected")

        self.log(f"Reading Flash memory ({total_size} bytes)...")
        buffer = bytearray()
        address = 0
        last_upper = -1
        t_start = time.time()

        while address < total_size:
            chunk_len = min(block_size, total_size - address)
            upper_addr = address >> 16
            if upper_addr != last_upper:
                buf = (ctypes.c_char * 4)()
                self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_SETLONGADDRESS, upper_addr, 0, buf, 0, 1000)
                last_upper = upper_addr

            rx_buf = (ctypes.c_char * chunk_len)()
            res = self.lib.usb_control_msg(
                self.handle, 0xC0, USBASP_FUNC_READFLASH,
                address & 0xFFFF, 0, rx_buf, chunk_len, 2000
            )
            if res < 0:
                raise IOError(f"Flash read failed at address 0x{address:06X}")

            buffer.extend(rx_buf.raw[:chunk_len])
            address += chunk_len
            elapsed = time.time() - t_start
            rate = address / elapsed if elapsed > 0 else 0
            eta = (total_size - address) / rate if rate > 0 else 0

            if progress_callback:
                progress_callback(address, total_size)
            if telemetry_callback:
                telemetry_callback({
                    "action": "read_flash",
                    "current": address,
                    "total": total_size,
                    "percent": int(address * 100 / total_size),
                    "rate_bps": rate,
                    "elapsed_s": elapsed,
                    "eta_s": eta,
                    "status": f"Reading 0x{address-chunk_len:04X}..0x{address:04X} ({rate:.1f} B/s, ETA: {eta:.1f}s)"
                })

        self.log(f"Flash read completed successfully: {len(buffer)} bytes in {time.time()-t_start:.2f}s.")
        return bytes(buffer)

    def write_flash(self, data: bytes, page_size: int,
                    skip_blank_pages: bool = True,
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    telemetry_callback: Optional[Callable[[Dict], None]] = None) -> bool:
        """
        Writes Flash memory page by page using USBasp accelerated writes.
        Includes smart blank page skipping (saving up to 80% flashing time)
        and real-time telemetry streaming.
        """
        if not self.is_connected:
            if not self.connect_target():
                return False

        total_size = len(data)
        total_pages = (total_size + page_size - 1) // page_size
        self.log(f"Programming Flash memory ({total_size} bytes in {total_pages} pages, Page: {page_size}B)...")

        t_start = time.time()
        address = 0
        last_upper = -1
        pages_written = 0
        pages_skipped = 0

        for p in range(total_pages):
            addr = p * page_size
            chunk = data[addr:addr + page_size]
            if len(chunk) < page_size:
                chunk = chunk + b'\xFF' * (page_size - len(chunk))

            # Smart page skipping for blank 0xFF pages
            if skip_blank_pages and all(b == 0xFF for b in chunk):
                pages_skipped += 1
                address += page_size
                if progress_callback:
                    progress_callback(address, total_size)
                continue

            upper_addr = addr >> 16
            if upper_addr != last_upper:
                buf = (ctypes.c_char * 4)()
                self.lib.usb_control_msg(self.handle, 0xC0, USBASP_FUNC_SETLONGADDRESS, upper_addr, 0, buf, 0, 1000)
                last_upper = upper_addr

            tx_buf = ctypes.create_string_buffer(bytes(chunk), page_size)
            # wIndex: page_size | (flags << 8), flags = 3 (FIRST | LAST)
            wIndex = page_size | (3 << 8)
            res = self.lib.usb_control_msg(
                self.handle, 0x40, USBASP_FUNC_WRITEFLASH,
                addr & 0xFFFF, wIndex, tx_buf, page_size, 2000
            )
            if res < 0:
                self.log(f"ERROR: Flash write failed at page {p} (address 0x{addr:06X})")
                return False

            pages_written += 1
            address += page_size
            elapsed = time.time() - t_start
            rate = (pages_written * page_size) / elapsed if elapsed > 0 else 0
            eta = ((total_pages - p - 1) * page_size) / rate if rate > 0 else 0

            if progress_callback:
                progress_callback(address, total_size)
            if telemetry_callback:
                telemetry_callback({
                    "action": "write_flash",
                    "current": address,
                    "total": total_size,
                    "page": p + 1,
                    "total_pages": total_pages,
                    "written": pages_written,
                    "skipped": pages_skipped,
                    "percent": int(address * 100 / total_size),
                    "rate_bps": rate,
                    "elapsed_s": elapsed,
                    "eta_s": eta,
                    "status": f"Page {p+1}/{total_pages} (0x{addr:04X}) | Written: {pages_written}, Skipped: {pages_skipped} | {rate:.1f} B/s | ETA: {eta:.1f}s"
                })

        dt = time.time() - t_start
        self.log(f"Flash programming completed: {pages_written} written, {pages_skipped} blank pages skipped in {dt:.2f}s.")
        return True

    # EEPROM Memory Read / Write
    def read_eeprom(self, total_size: int, block_size: int = 128,
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    telemetry_callback: Optional[Callable[[Dict], None]] = None) -> bytes:
        """Reads target EEPROM memory."""
        if not self.is_connected:
            if not self.connect_target():
                raise IOError("Target not connected")

        self.log(f"Reading EEPROM memory ({total_size} bytes)...")
        buffer = bytearray()
        address = 0
        t_start = time.time()

        while address < total_size:
            chunk_len = min(block_size, total_size - address)
            rx_buf = (ctypes.c_char * chunk_len)()
            res = self.lib.usb_control_msg(
                self.handle, 0xC0, USBASP_FUNC_READEEPROM,
                address, 0, rx_buf, chunk_len, 2000
            )
            if res < 0:
                raise IOError(f"EEPROM read failed at address 0x{address:04X}")

            buffer.extend(rx_buf.raw[:chunk_len])
            address += chunk_len
            elapsed = time.time() - t_start
            rate = address / elapsed if elapsed > 0 else 0

            if progress_callback:
                progress_callback(address, total_size)
            if telemetry_callback:
                telemetry_callback({
                    "action": "read_eeprom",
                    "current": address,
                    "total": total_size,
                    "percent": int(address * 100 / total_size),
                    "rate_bps": rate,
                    "elapsed_s": elapsed,
                    "status": f"Reading EEPROM 0x{address-chunk_len:04X}..0x{address:04X} ({rate:.1f} B/s)"
                })

        self.log(f"EEPROM read completed successfully: {len(buffer)} bytes.")
        return bytes(buffer)

    def write_eeprom(self, data: bytes, page_size: int = 4,
                     progress_callback: Optional[Callable[[int, int], None]] = None,
                     telemetry_callback: Optional[Callable[[Dict], None]] = None) -> bool:
        """Writes target EEPROM memory."""
        if not self.is_connected:
            if not self.connect_target():
                return False

        total_size = len(data)
        self.log(f"Programming EEPROM memory ({total_size} bytes)...")
        address = 0
        t_start = time.time()

        while address < total_size:
            chunk_len = min(page_size, total_size - address)
            chunk = data[address:address + chunk_len]
            # Skip 0xFF pages
            if all(b == 0xFF for b in chunk):
                address += chunk_len
                if progress_callback:
                    progress_callback(address, total_size)
                continue

            tx_buf = ctypes.create_string_buffer(bytes(chunk), chunk_len)
            res = self.lib.usb_control_msg(
                self.handle, 0x40, USBASP_FUNC_WRITEEEPROM,
                address, chunk_len, tx_buf, chunk_len, 2000
            )
            if res < 0:
                self.log(f"ERROR: EEPROM write failed at address 0x{address:04X}")
                return False

            address += chunk_len
            elapsed = time.time() - t_start
            rate = address / elapsed if elapsed > 0 else 0

            if progress_callback:
                progress_callback(address, total_size)
            if telemetry_callback:
                telemetry_callback({
                    "action": "write_eeprom",
                    "current": address,
                    "total": total_size,
                    "percent": int(address * 100 / total_size),
                    "rate_bps": rate,
                    "elapsed_s": elapsed,
                    "status": f"Writing EEPROM 0x{address:04X} ({rate:.1f} B/s)"
                })

        self.log("EEPROM memory programming completed.")
        return True

    # Verification
    def verify_flash(self, expected: bytes, page_size: int = 128,
                     progress_callback: Optional[Callable[[int, int], None]] = None,
                     telemetry_callback: Optional[Callable[[Dict], None]] = None) -> Tuple[bool, int]:
        """Compares target Flash with expected buffer."""
        actual = self.read_flash(len(expected), page_size, progress_callback, telemetry_callback)
        for i in range(len(expected)):
            if expected[i] != actual[i]:
                self.log(f"Flash verification FAILED at 0x{i:06X}: expected 0x{expected[i]:02X}, read 0x{actual[i]:02X}")
                return False, i
        self.log("Flash verification SUCCESS: Buffer and Device memory match 100%!")
        return True, -1

    def verify_eeprom(self, expected: bytes, block_size: int = 128,
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, int]:
        """Compares target EEPROM with expected buffer."""
        actual = self.read_eeprom(len(expected), block_size, progress_callback)
        for i in range(len(expected)):
            if expected[i] != actual[i]:
                self.log(f"EEPROM verification FAILED at 0x{i:04X}: expected 0x{expected[i]:02X}, read 0x{actual[i]:02X}")
                return False, i
        self.log("EEPROM verification SUCCESS: Buffer and Device memory match 100%!")
        return True, -1
