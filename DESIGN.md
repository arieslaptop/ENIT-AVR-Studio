# ENIT AVR Studio — Design System Specification
**Version**: 1.0.0 (Master Desktop Specification)  
**Author**: Aries Computer Solutions, Harshad Patel, India  
**Design Engine**: Google Stitch MCP (`projects/12372459068504462501`)  
**Design Asset ID**: `assets/18ccfdfc57254fa28e758874942f328a`  
**Copyright**: &copy; 2026 Aries Computer Solutions. All Rights Reserved.

---

## 1. Brand & Aesthetic Vision

The ENIT AVR Studio design system embodies precision-grade embedded systems engineering. Crafted for firmware architects, electrical engineers, and hardware security researchers, the aesthetic projects computational rigor, absolute determinism, and surgical telemetry monitoring.

The design movement merges **Tactile Industrial Brutalism** with **Modern Cybernetic Technical HUD styling**. Surfaces are dense, deliberate, and mathematically aligned, eliminating ornamental fluff in favor of high-legibility telemetry, segmented memory tables, and reactive signal indicators. The visual tone balances mission-critical instrument readouts with the sleek ergonomics of modern native IDE suites.

---

## 2. Color Palette & Chromatic Tokens

The palette operates on strict chromatic tiering designed for long-shift diagnostic concentration and zero eye fatigue under low ambient light:

### 2.1 Base Surfaces & Viewports
| Token | Hex Value | Semantic Role |
|:---|:---:|:---|
| `surface-void` | `#11141c` | Root Canvas / Void behind docked panes |
| `surface-level-1` | `#171b26` | Toolbars, Dock Panels, Card backgrounds |
| `surface-level-2` | `#1e2433` | Inspector Cards, Dock Headers, Flyouts |
| `surface-active` | `#2a3348` | Active row selections, High-contrast borders |
| `surface-input` | `#090d16` | Monospace code editors, input fields |

### 2.2 Interactive Signals & Accents
| Token | Hex Value | Semantic Role |
|:---|:---:|:---|
| `primary-accent` | `#00adb5` | Luminous Cyan: Execution Pointers, Active Registers, Primary Brand |
| `primary-bright` | `#55d8e1` | Highlighted Cyan: Interactive hover states, Active status LED |
| `secondary-accent` | `#38bdf8` | Electric Sky: Data bus flow, Memory offsets, Tab active borders |
| `tertiary-accent` | `#10b981` | Emerald Telemetry: Logic HIGH, Flash verified, Read All success |
| `danger-accent` | `#dc2626` | Crimson Trigger: Write All, Chip Erase, Overwrite warnings |
| `danger-glow` | `#ef4444` | High-priority pulse, verification mismatch |
| `warning-alert` | `#f59e0b` | Amber Alert: Dirty memory bytes, uncommitted fuse edits |
| `dormant-slate` | `#475569` | Logic LOW, Unchecked bits, Inactive registers |

### 2.3 Text & Typography Contrast
| Token | Hex Value | Semantic Role |
|:---|:---:|:---|
| `text-primary` | `#f1f5f9` | 95% Bright White Slate: Opcodes, Hex data, Primary headings |
| `text-secondary` | `#94a3b8` | Muted Cyanic Gray: Labels, Column headers, Metadata |
| `text-disabled` | `#64748b` | Muted Slate: Inactive assembly, comments |

---

## 3. Typography Hierarchy

Typographic discipline prioritizes instant scanning, strict character alignment, and zero ambiguity between visually similar glyphs (such as `0` vs `O`, `1` vs `l` vs `I`).

| Style | Font Family | Size | Weight | Line Height | Usage |
|:---|:---|:---:|:---:|:---:|:---|
| `headline-lg` | Inter / Segoe UI | 22px | 700 | 28px | Main Application Title |
| `headline-md` | Inter / Segoe UI | 16px | 600 | 22px | Section Group Boxes & Cards |
| `headline-sm` | Inter / Segoe UI | 14px | 600 | 20px | Dialog Headers, Tab Titles |
| `body-md` | Inter / Segoe UI | 13px | 400 | 18px | Descriptive text, Instructions |
| `body-sm` | Inter / Segoe UI | 11px | 400 | 15px | Help footnotes, Copyright banner |
| `code-lg` | JetBrains Mono / Consolas | 14px | 600 | 20px | Hex values (Fuses, Signatures) |
| `code-md` | JetBrains Mono / Consolas | 12px | 500 | 16px | 16-byte Hex Editor Data Matrix |
| `code-sm` | JetBrains Mono / Consolas | 11px | 400 | 14px | Timestamped Console Logs |
| `label-badge` | JetBrains Mono / Consolas | 10px | 600 | 12px | Status Pills, Rate Gauges, CRC32 |

---

## 4. Spacing & Dimensional Scales

- **Base Grid Unit**: 4px (`0.25rem`)
- **Card Margins**: 8px (`0.5rem`)
- **Panel Gutter**: 6px–10px
- **Button Heights**: Standard `28px`, Compact `24px`, Hero Action `34px`
- **Corner Radii**: Standard `4px` (machined chassis finish), Pills `9999px`, Dialogs `8px`
- **Hex Editor Row Height**: Strict `22px` for maximum high-density memory inspection

---

## 5. Component Specifications

### 5.1 Hardware Triggers & Action Buttons
- **Primary / Connect (`#00adb5`)**: Sharp 4px corner radius, dark text `#11141c`, bold weight.
- **Success / Read All (`#059669` / `#10b981`)**: Emerald gradient, white text.
- **Danger / Write All / Erase (`#dc2626`)**: Crimson background, white text, 1px `#ef4444` border.
- **Secondary / Tools (`#1e2433`)**: Slate background, 1px `#2a3348` border, text `#f1f5f9`.

### 5.2 16-Byte Hex Matrix Editor
- **Address Column (0x000000)**: `#64748b` monospace.
- **Byte Columns (00..0F)**: `#f1f5f9` centered with grouped 4-byte micro-gutters.
- **ASCII Representation Panel**: Monospace characters pinned to right margin.
- **Modified / Dirty Cell**: Amber `#f59e0b` text.

### 5.3 Live Telemetry HUD Ribbon
- **Container**: Obsidian slate `#0b0f19` with hairline border `#1e293b`.
- **Active Speed**: Bold emerald/cyan typography with instantaneous B/s and KB/s throughput.
- **Progress Bar**: Dual-tone gradient chunk (`#0284c7` to `#00adb5`) with animated micro-sheen.
- **Hardware Pill**: Pulsing green dot with real-time target signature verification.

### 5.4 Modal Dialogs (`EnitConfirmDialog`, `ZIFPlacementDialog`, `BitDetailsDialog`)
- Guaranteed 100% dark mode compliance via Qt Fusion engine + custom palette.
- High-contrast text `#f8fafc` on dark slate `#171b26`, completely eliminating Windows light-mode bleaching.

