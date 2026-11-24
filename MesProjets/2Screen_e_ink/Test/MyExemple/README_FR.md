# Fontes vectorielles Hershey pour MicroPython / MCU

Chaîne de transformation de fontes vectorielles inspirée des **fontes Hershey à simple trait**, conçue pour **MicroPython** et les **microcontrôleurs**, avec un accent mis sur la **simplicité**, la **pédagogie** et une **complexité nulle à l'exécution**.


source utile:
https://gitlab.com/oskay/svg-fonts/-/blob/master/fonts/Hershey/HersheyGothGerman.svg?ref_type=heads
https://wiki.evilmadscientist.com/Hershey_Text

---

## ✨ Pourquoi ce projet ?

Afficher du texte sur un microcontrôleur devient rapidement complexe si l'on part de formats classiques comme **TTF** ou **OTF** :

- formats trop complexes à parser
- empreinte mémoire importante
- conçus pour des systèmes avec OS complet

Ce projet apporte :

✅ **Un format de fonte vectorielle simple**  
✅ **Des glyphes uniquement composés de segments (style Hershey)**  
✅ **Une mise à l'échelle libre**  
✅ **Aucun calcul flottant à l'exécution**  
✅ **Compatible MicroPython**  
✅ **Lisible, pédagogique et débogable**

---

## 🧠 Principe fondamental

> Une police n'est **ni une image**, ni une courbe.  
> Une police est **un ensemble de segments de droites**.

Chaque caractère (glyphe) est défini par :
- une largeur d'avance
- une liste de segments
- chaque segment est de la forme `(x1, y1) → (x2, y2)`

Ce principe est celui des **fontes Hershey historiques**, adapté ici à un usage moderne et embarqué.

---

## 🛠️ Chaîne de transformation

```text
Fonte Hershey SVG (Inkscape)
        ↓
Conversion Python hors ligne
        ↓
──────────────────────────
│  fonte.bin → production
│  fonte.py  → debug / pédagogie
──────────────────────────
        ↓
Moteur de rendu unique
```

⚠️ **Le SVG n'est jamais analysé sur le microcontrôleur**.  
Tout le travail complexe est effectué **hors ligne sur PC**.

---

## 📁 Structure du dépôt

```text
.
├── svg_to_hershey.py        # Convertisseur SVG → .bin + .py
├── examples/
│   ├── hershey_gothic.svg
│   ├── hershey_gothic.bin
│   └── hershey_gothic.py
└── README.md
```

---

## ✏️ Source des fontes : SVG (Inkscape)

Les fontes sont créées ou modifiées avec **Inkscape** et l'extension  
**"Hershey Text" d'Evil Mad Scientist** :

👉 https://wiki.evilmadscientist.com/Hershey_Text

Le SVG sert **uniquement de format source**.

Fonctionnalités SVG prises en charge :
- `<font>`, `<font-face>`, `<glyph>`
- commandes de chemin `M` (move), `L` (line)

Ignoré volontairement :
- courbes
- remplissages
- transformations
- arcs

---

## 🔄 Script de conversion

### `svg_to_hershey.py`

Ce script :

- parcourt tous les fichiers `.svg` du répertoire
- génère **deux fichiers par fonte** :
  - `fonte.bin` → format de production
  - `fonte.py`  → format lisible et importable

Exécution :

```bash
python svg_to_hershey.py
```

---

## 📦 Formats de sortie

### 1️⃣ `fonte.bin` – format binaire de production

Format compact destiné à être stocké en Flash sur MCU.

Structure conceptuelle :

```text
EN-TÊTE
  uint16 nombre_de_glyphes
  int16  ascent
  int16  descent

TABLE D'INDEX
  unicode → offset

DONNÉES GLYPHES
  advance
  nombre_de_segments
  (x1,y1,x2,y2) × N
```

✅ très compact  
✅ très rapide  
✅ aucun parsing texte  
✅ pas d'allocation dynamique  

---

### 2️⃣ `fonte.py` – format lisible & pédagogique

Représentation **Python pure**, totalement compatible avec **MicroPython**.

Exemple :

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

✅ lisible  
✅ importable  
✅ idéal pour le debug  
✅ même moteur de rendu que le `.bin`

---

## 🧮 Système de coordonnées

- origine : **ligne de base du caractère**
- plage des unités : `[-127 … +127]`
- l'échelle est appliquée au rendu

```python
x_ecran = x + x1 * scale
y_ecran = y - y1 * scale
```

✅ calculs entiers uniquement  
✅ aucun flottant requis  

---

## 🖍️ Rendu (pseudo-code)

Le **même moteur de rendu** fonctionne pour les formats `.bin` et `.py` :

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

## 🎓 Pourquoi ce format est pédagogique

Il permet de comprendre :

- une police comme une géométrie
- la correspondance Unicode → glyphe
- la ligne de base, l'ascent et le descent
- l'application d'échelles
- la séparation **compilation / exécution**

> Si vous savez tracer des lignes, vous savez afficher du texte.

---

## 🔮 Extensions possibles

Sans changer le format :
- composition d'accents
- épaisseur de trait
- mise en cache
- sous-ensembles Unicode
- fontes UI dédiées

---

## 📜 Licence & crédits

- Inspiré par les **fontes vectorielles Hershey**
- Compatible avec les fontes dérivées distribuées par  
  Evil Mad Scientist et projets associés
- Code de conversion et format : **libre et orienté MIT**

---

## ✅ État du projet

✔ Format stable  
✔ Compatible MicroPython  
✔ Orienté pédagogie  
✔ Prêt pour l'embarqué  

---

Si vous souhaitez :
- un moteur de rendu MicroPython prêt à l'emploi
- des exemples sur matériel réel
- un tutoriel pas à pas

👉 ouvrez une issue ou démarrez une discussion 🚀
