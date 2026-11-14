# Hershey Vector Fonts for MicroPython / MCU

Vector font pipeline inspired by **Hershey single‑stroke fonts**, designed for **MicroPython** and **microcontrollers**, with an emphasis on **simplicity**, **pedagogy**, and **zero runtime complexity**.

---

## ✨ Why this project?

Rendering text on a microcontroller is surprisingly hard if you start with desktop formats such as **TTF** or **OTF**:

- too complex to parse
- heavy memory footprint
- designed for full operating systems, not MCUs

This project provides:

✅ **A simple vector font format**  
✅ **Line‑only glyphs (Hershey style)**  
✅ **Scalable at any size**  
✅ **No floating point at runtime**  
✅ **MicroPython‑friendly**  
✅ **Pedagogical and debuggable**

---

## 🧠 Core idea

> A font is **not a bitmap** and **not a curve**.  
> A font is **a set of straight line segments**.

Each character (glyph) is defined by:
- an advance width
- a list of line segments  
- each segment is `(x1, y1) → (x2, y2)`

This is exactly the philosophy behind the original **Hershey fonts**, adapted here to modern embedded workflows.

---

## 🛠️ Workflow overview

```text
SVG Hershey Font (Inkscape)
        ↓
Offline Python conversion
        ↓
──────────────────────────
│  font.bin  → production
│  font.py   → debug / doc
──────────────────────────
        ↓
Single rendering engine
```

⚠️ **SVG is never parsed on the microcontroller**.  
All heavy work is done **offline on a PC**.

---

## 📁 Repository structure

```text
.
├── svg_to_hershey.py        # SVG → .bin + .py converter
├── examples/
│   ├── hershey_gothic.svg
│   ├── hershey_gothic.bin
│   └── hershey_gothic.py
└── README.md
```

---

## ✏️ Font source: SVG (Inkscape)

Fonts are designed or edited using **Inkscape** with the  
**Evil Mad Scientist “Hershey Text” extension**:

👉 https://wiki.evilmadscientist.com/Hershey_Text

The SVG **serves only as a source format**.

Supported SVG features:
- `<font>`, `<font-face>`, `<glyph>`
- path commands: `M` (move), `L` (line)

Ignored:
- curves
- fills
- transforms
- arcs

---

## 🔄 Conversion script

### `svg_to_hershey.py`

This script:

- scans all `.svg` files in the directory
- generates **two outputs per font**:
  - `font.bin` → production format
  - `font.py`  → readable, importable debug format

Run it with:

```bash
python svg_to_hershey.py
```

---

## 📦 Output formats

### 1️⃣ `font.bin` — production format

A compact binary format intended for MCU flash usage.

Structure (conceptual):

```text
HEADER
  uint16 glyph_count
  int16  ascent
  int16  descent

INDEX TABLE
  unicode → offset

GLYPH DATA
  advance
  segment_count
  (x1,y1,x2,y2) × N
```

✅ very compact  
✅ very fast  
✅ no text parsing  
✅ no dynamic allocation  

---

### 2️⃣ `font.py` — debug & pedagogical format

A **pure Python representation**, fully compatible with **MicroPython**.

Example:

```python
FONT_HEADER = {
    "glyph_count": 423,
    "ascent": 800,
    "descent": -200,
}

GLYPH_INDEX = {
    0x0041: (0, 12, 3),  # 'A'
}

GLYPH_DATA = [
    (
        12,
        (
            (-15,  80,   0, 120),
            ( 15,  80,   0, 120),
            (-10, 100,  10, 100),
        )
    ),
]
```

✅ fully readable  
✅ importable  
✅ debuggable  
✅ uses the **same rendering logic as `.bin`**

---

## 🧮 Coordinate system

- origin: **baseline of the glyph**
- unit range: `[-127 … +127]`
- scaling is applied at render time

```python
x_screen = x + x1 * scale
y_screen = y - y1 * scale
```

✅ integer‑only arithmetic  
✅ no floating point required  

---

## 🖍️ Rendering (pseudo‑code)

The **same rendering engine** works for both `.bin` and `.py`:

```python
glyph_id, adv, _ = GLYPH_INDEX[unicode]
advance, segments = GLYPH_DATA[glyph_id]

for x1, y1, x2, y2 in segments:
    draw_line(
        x + x1 * scale,
        y - y1 * scale,
        x + x2 * scale,
        y - y2 * scale
    )

x += adv * scale
```

---

## 🎓 Why this is pedagogical

This project helps learners understand:

- fonts as geometry, not images
- Unicode mapping
- baseline / ascent / descent
- scaling and transformations
- separation of **compile‑time vs runtime complexity**

> If you can draw lines, you can draw text.

---

## 🔮 Future extensions

Without changing the format:
- glyph composition (accents)
- stroke thickness
- caching
- partial Unicode subsets
- custom UI fonts

---

## 📜 License & Credits

- Based on the **Hershey vector font philosophy**
- Compatible with Hershey‑derived fonts distributed by  
  Evil Mad Scientist and related projects
- Conversion code and format: **MIT‑style friendly**

---

## ✅ Status

✔ Format stable  
✔ MicroPython‑friendly  
✔ Educational  
✔ MCU‑ready  

---

If you want:
- a MicroPython rendering engine
- examples on real boards
- or a tutorial for beginners

👉 open an issue or start a discussion 🚀
