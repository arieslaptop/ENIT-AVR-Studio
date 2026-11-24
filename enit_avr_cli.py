"""
================================================================================
ENIT AVR STUDIO - Command Line Interface (CLI)
Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India
All Rights Reserved.
================================================================================
"""

import argparse
import os
import sys
import time

from enit_avr_core import SCK_SPEEDS, USBaspProgrammer
from enit_chip_db import CHIP_DATABASE, find_by_name, find_by_signature
from enit_hex_parser import IntelHex

def print_banner():
    print("=" * 72)
    print("   ENIT AVR STUDIO - Professional Microcontroller Programmer CLI")
    print("   Copyright (C) 2026 Aries Computer Solutions, Harshad Patel, India")
    print("=" * 72)

def main():
    parser = argparse.ArgumentParser(
        description="ENIT AVR Studio CLI - Flash, EEPROM, and Fuse Programmer for AVR Microcontrollers"
    )
    parser.add_argument("-c", "--chip", help="Target chip model (e.g. ATmega328P, ATmega16, ATmega8)")
    parser.add_argument("-p", "--detect", action="store_true", help="Auto-detect connected target chip")
    parser.add_argument("-s", "--speed", default="Auto", choices=list(SCK_SPEEDS.keys()), help="ISP SCK Speed")
    parser.add_argument("-e", "--erase", action="store_true", help="Perform chip erase")
    parser.add_argument("-rf", "--read-flash", metavar="OUT.HEX", help="Read Flash memory to Intel HEX file")
    parser.add_argument("-wf", "--write-flash", metavar="IN.HEX", help="Write Intel HEX file to Flash memory")
    parser.add_argument("-vf", "--verify-flash", metavar="IN.HEX", help="Verify Flash against Intel HEX file")
    parser.add_argument("-re", "--read-eeprom", metavar="OUT.EEP", help="Read EEPROM to EEP/HEX file")
    parser.add_argument("-we", "--write-eeprom", metavar="IN.EEP", help="Write EEP/HEX file to EEPROM")
    parser.add_argument("-rF", "--read-fuses", action="store_true", help="Read current Fuse & Lock bit values")
    parser.add_argument("-wF", "--write-fuses", metavar="LF:HF:EF:LK",
                        help="Write fuse bytes formatted as hex, e.g. FF:DE:FD:FF")
    parser.add_argument("--write-all", action="store_true",
                        help="Write All: Erase chip, write Flash (-wf), EEPROM (-we), and Fuses (-wF)")

    args = parser.parse_args()
    print_banner()

    prog = USBaspProgrammer(log_callback=print)

    if not prog.open():
        sys.exit(1)

    if not prog.connect_target():
        prog.close()
        sys.exit(1)

    try:
        if args.speed != "Auto":
            prog.set_sck_speed(SCK_SPEEDS[args.speed])

        # Identify chip
        chip = None
        if args.detect or not args.chip:
            chip = prog.autodetect_chip()
        elif args.chip:
            chip = find_by_name(args.chip)
            if not chip:
                print(f"Error: Unknown chip model '{args.chip}'.")
                sys.exit(1)
            sig = prog.read_signature()
            if sig != chip.signature:
                print(f"WARNING: Chip signature [0x{sig[0]:02X}, 0x{sig[1]:02X}, 0x{sig[2]:02X}] does NOT match {chip.name} signature {chip.signature}!")

        if not chip:
            print("Error: Could not identify target chip.")
            sys.exit(1)

        print(f"\n[+] Active Device: {chip.name}")
        print(f"    Flash Memory:  {chip.flash_size} Bytes ({chip.flash_size // 1024} KB)")
        print(f"    EEPROM Memory: {chip.eeprom_size} Bytes")
        print(f"    Page Size:     {chip.page_size} Bytes\n")

        # Telemetry printer
        def on_telem(t):
            action = t.get("action", "")
            if action == "write_flash":
                print(f"\r[TELEMETRY] Write Flash: Page {t.get('page')}/{t.get('total_pages')} | {t.get('percent')}% | {t.get('rate_bps', 0):.1f} B/s | ETA: {t.get('eta_s', 0):.1f}s", end='', flush=True)
            elif action == "read_flash":
                print(f"\r[TELEMETRY] Read Flash: {t.get('current')}/{t.get('total')} bytes ({t.get('percent')}%) | {t.get('rate_bps', 0):.1f} B/s", end='', flush=True)

        # 1. Chip Erase
        if args.erase or args.write_all:
            print("[*] Step: Executing Bulk Chip Erase...")
            if prog.chip_erase():
                print("[+] Chip Erase SUCCESS.")
            else:
                print("[-] Chip Erase FAILED.")
                sys.exit(1)

        # 2. Write Flash
        if args.write_flash:
            hex_file = IntelHex(size=chip.flash_size)
            cnt, highest = hex_file.load_hex_file(args.write_flash)
            print(f"[+] Loaded {cnt} bytes from {args.write_flash} (Max Addr: 0x{highest:04X})")
            data = bytes(hex_file.buffer[:highest + 1])
            prog.write_flash(data, chip.page_size, skip_blank_pages=True, telemetry_callback=on_telem)
            print("\n[+] Flash write complete.")
            # Auto-verify
            print("[*] Verifying Flash memory...")
            ok, err_addr = prog.verify_flash(data, chip.page_size)
            if not ok:
                print(f"[-] Verification failed at 0x{err_addr:06X}")
                sys.exit(1)
            print("[+] Flash verified successfully (100% match).")

        # 3. Write EEPROM
        if args.write_eeprom:
            hex_file = IntelHex(size=chip.eeprom_size)
            if args.write_eeprom.lower().endswith('.bin'):
                cnt = hex_file.load_binary_file(args.write_eeprom)
            else:
                cnt, _ = hex_file.load_hex_file(args.write_eeprom)
            data = bytes(hex_file.buffer[:chip.eeprom_size])
            prog.write_eeprom(data, 4, telemetry_callback=on_telem)
            print("\n[+] EEPROM write complete.")

        # 4. Write Fuses
        if args.write_fuses:
            parts = args.write_fuses.split(':')
            lf = int(parts[0], 16) if len(parts) > 0 and parts[0] else None
            hf = int(parts[1], 16) if len(parts) > 1 and parts[1] else None
            ef = int(parts[2], 16) if len(parts) > 2 and parts[2] else None
            lk = int(parts[3], 16) if len(parts) > 3 and parts[3] else None
            print(f"[*] Writing Fuses: LF={hex(lf) if lf else '-'}, HF={hex(hf) if hf else '-'}, EF={hex(ef) if ef else '-'}, Lock={hex(lk) if lk else '-'}")
            prog.write_fuses(lf, hf, ef, lk)

        # 5. Read Fuses
        if args.read_fuses or not (args.write_flash or args.write_eeprom or args.read_flash or args.read_eeprom):
            fuses = prog.read_fuses()
            print(f"[+] Low Fuse:      0x{fuses['low']:02X}")
            print(f"[+] High Fuse:     0x{fuses['high']:02X}")
            print(f"[+] Extended Fuse: 0x{fuses['ext']:02X}")
            print(f"[+] Lock Byte:     0x{fuses['lock']:02X}")
            print(f"[+] Calibration:   0x{fuses['calib']:02X}")

        # 6. Read Flash
        if args.read_flash:
            data = prog.read_flash(chip.flash_size, chip.page_size, telemetry_callback=on_telem)
            print("\n[+] Flash read complete.")
            hex_file = IntelHex(size=chip.flash_size)
            hex_file.buffer = bytearray(data)
            hex_file.save_hex_file(args.read_flash)
            print(f"[+] Saved {len(data)} bytes to {args.read_flash}")

        # 7. Read EEPROM
        if args.read_eeprom:
            data = prog.read_eeprom(chip.eeprom_size, 128, telemetry_callback=on_telem)
            print("\n[+] EEPROM read complete.")
            hex_file = IntelHex(size=chip.eeprom_size)
            hex_file.buffer = bytearray(data)
            hex_file.save_hex_file(args.read_eeprom)
            print(f"[+] Saved {len(data)} bytes to {args.read_eeprom}")

    finally:
        prog.disconnect_target()
        prog.close()

if __name__ == "__main__":
    main()
