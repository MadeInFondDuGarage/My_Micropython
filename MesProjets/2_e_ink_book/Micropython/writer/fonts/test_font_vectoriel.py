WIDTH  = 200
HEIGHT = 60

# Buffer texte simple (visualisable dans la console)
buffer = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]


def draw_line(x1, y1, x2, y2):
    """Dessin d'une ligne (algorithme de Bresenham simplifié)"""
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy

    while True:
        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            buffer[y1][x1] = "#"

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy

def draw_text(x, y, text, scale=1):
    """
    Dessine un texte vectoriel Hershey.
    (x, y) = position de départ (ligne de base)
    scale  = facteur de mise à l'échelle
    """
    cx = x  # curseur horizontal

    for ch in text:
        code = ord(ch)

        if code not in font.GLYPH_INDEX:
            cx += 4 * scale  # espace par défaut
            continue

        glyph_id, advance, _ = font.GLYPH_INDEX[code]
        adv, segments = font.GLYPH_DATA[glyph_id]

        for x1, y1, x2, y2 in segments:
            draw_line(
                cx + x1 * scale,
                y  - y1 * scale,
                cx + x2 * scale,
                y  - y2 * scale,
            )

        cx += advance * scale
        
import HersheySansMed as font

draw_text(x=10,y=40,text="Bonjour",scale=1)

for row in buffer:
    print("".join(row))

