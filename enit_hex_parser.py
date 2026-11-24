"""
================================================================================
ENIT AVR STUDIO - Intel HEX & EEPROM Parser Module
Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India
All Rights Reserved.
================================================================================
"""

import os
from typing import Tuple, Dict, Optional, List

class IntelHex:
    """
    Robust Intel HEX parser and generator for AVR Flash and EEPROM buffers.
    Supports record types:
      00 - Data Record
      01 - End of File Record
      02 - Extended Segment Address Record
      04 - Extended Linear Address Record
    """

    def __init__(self, size: int = 32768, fill_byte: int = 0xFF):
        self.size = size
        self.fill_byte = fill_byte
        self.buffer = bytearray([fill_byte] * size)
        self.min_addr = 0
        self.max_addr = 0
        self.has_data = False

    def clear(self, fill_byte: Optional[int] = None):
        if fill_byte is None:
            fill_byte = self.fill_byte
        self.buffer = bytearray([fill_byte] * self.size)
        self.min_addr = 0
        self.max_addr = 0
        self.has_data = False

    def resize(self, new_size: int, fill_byte: Optional[int] = None):
        if fill_byte is None:
            fill_byte = self.fill_byte
        if new_size > len(self.buffer):
            self.buffer.extend(bytearray([fill_byte] * (new_size - len(self.buffer))))
        elif new_size < len(self.buffer):
            self.buffer = self.buffer[:new_size]
        self.size = new_size

    def load_hex_file(self, file_path: str) -> Tuple[int, int]:
        """
        Parses an Intel HEX file into the memory buffer.
        Returns: (bytes_loaded, highest_address)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HEX file not found: {file_path}")

        extended_address = 0
        bytes_loaded = 0
        highest_address = 0
        lowest_address = 0xFFFFFFFF
        eof_found = False

        with open(file_path, 'r', encoding='ascii', errors='ignore') as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                if not line.startswith(':'):
                    continue

                if len(line) < 11:
                    raise ValueError(f"Line {line_no}: Corrupt Intel HEX record (too short)")

                try:
                    record_bytes = bytes.fromhex(line[1:])
                except ValueError as ex:
                    raise ValueError(f"Line {line_no}: Non-hexadecimal characters detected: {ex}")

                # Verify checksum: sum of all bytes modulo 256 must equal 0
                if sum(record_bytes) & 0xFF != 0:
                    raise ValueError(f"Line {line_no}: Checksum mismatch in Intel HEX record")

                byte_count = record_bytes[0]
                address = (record_bytes[1] << 8) | record_bytes[2]
                record_type = record_bytes[3]
                data = record_bytes[4:4 + byte_count]

                if len(data) != byte_count:
                    raise ValueError(f"Line {line_no}: Record length mismatch")

                if record_type == 0x00:  # Data record
                    abs_addr = extended_address + address
                    for i, b in enumerate(data):
                        curr_addr = abs_addr + i
                        if curr_addr >= len(self.buffer):
                            # Auto-expand if needed
                            self.resize(max(curr_addr + 1024, len(self.buffer) * 2))
                        self.buffer[curr_addr] = b
                        bytes_loaded += 1
                        if curr_addr > highest_address:
                            highest_address = curr_addr
                        if curr_addr < lowest_address:
                            lowest_address = curr_addr

                elif record_type == 0x01:  # EOF record
                    eof_found = True
                    break

                elif record_type == 0x02:  # Extended Segment Address Record
                    extended_address = ((data[0] << 8) | data[1]) << 4

                elif record_type == 0x04:  # Extended Linear Address Record
                    extended_address = ((data[0] << 8) | data[1]) << 16

                elif record_type in (0x03, 0x05):  # Start Segment / Start Linear Address
                    continue  # Ignore start execution address for MCU ROM
                else:
                    raise ValueError(f"Line {line_no}: Unsupported record type 0x{record_type:02X}")

        if not eof_found and bytes_loaded == 0:
            raise ValueError("No valid Intel HEX records or EOF found.")

        self.min_addr = lowest_address if lowest_address != 0xFFFFFFFF else 0
        self.max_addr = highest_address
        self.has_data = bytes_loaded > 0
        return bytes_loaded, highest_address

    def save_hex_file(self, file_path: str, max_address: Optional[int] = None, line_length: int = 16):
        """
        Exports the memory buffer into Intel HEX format.
        """
        if max_address is None:
            max_address = len(self.buffer) - 1

        with open(file_path, 'w', encoding='ascii') as f:
            current_ext_addr = -1
            addr = 0
            while addr <= max_address:
                # Check 64KB boundary
                upper_addr = addr >> 16
                if upper_addr != current_ext_addr:
                    current_ext_addr = upper_addr
                    # Write type 04 record
                    data_ext = bytes([(current_ext_addr >> 8) & 0xFF, current_ext_addr & 0xFF])
                    rec = bytearray([0x02, 0x00, 0x00, 0x04]) + data_ext
                    checksum = (-sum(rec)) & 0xFF
                    f.write(f":02000004{data_ext.hex().upper()}{checksum:02X}\n")

                chunk_len = min(line_length, max_address - addr + 1)
                chunk = self.buffer[addr:addr + chunk_len]
                local_addr = addr & 0xFFFF
                rec = bytearray([chunk_len, (local_addr >> 8) & 0xFF, local_addr & 0xFF, 0x00]) + chunk
                checksum = (-sum(rec)) & 0xFF
                f.write(f":{chunk_len:02X}{local_addr:04X}00{chunk.hex().upper()}{checksum:02X}\n")
                addr += chunk_len

            # End of file record
            f.write(":00000001FF\n")

    def load_binary_file(self, file_path: str) -> int:
        """Loads a raw binary file directly into buffer."""
        with open(file_path, 'rb') as f:
            data = f.read()
        if len(data) > len(self.buffer):
            self.resize(len(data))
        self.buffer[:len(data)] = data
        self.min_addr = 0
        self.max_addr = len(data) - 1
        self.has_data = True
        return len(data)

    def save_binary_file(self, file_path: str, length: Optional[int] = None):
        """Saves buffer as raw binary."""
        if length is None:
            length = len(self.buffer)
        with open(file_path, 'wb') as f:
            f.write(self.buffer[:length])

