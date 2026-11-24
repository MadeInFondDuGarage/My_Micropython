# vec_player.py - Lecteur MicroPython pour dessin vectoriel (.py)

def render_py_drawing(drawing_mod, canvas, ox=0, oy=0):
    """Dessine un module généré (ex: import dessin) avec décalage (ox, oy)."""
    for op, filled, color, sw, params in drawing_mod.CMDS:
        if op == drawing_mod.RECT:
            x, y, w, h = params
            canvas.rect(x + ox, y + oy, w, h, color, filled, sw)

        elif op == drawing_mod.CIRCLE:
            cx, cy, r = params
            canvas.circle(cx + ox, cy + oy, r, color, filled, sw)

        elif op == drawing_mod.LINE:
            x1, y1, x2, y2 = params
            canvas.line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, color, sw)

        elif op == drawing_mod.TRI:
            x1, y1, x2, y2, x3, y3 = params
            canvas.tri(
                x1 + ox, y1 + oy,
                x2 + ox, y2 + oy,
                x3 + ox, y3 + oy,
                color, filled, sw,
            )

        elif op == drawing_mod.POLY:
            # params est une tuple à 1 élément contenant la tuple de points ((x,y), ...)
            raw_pts = params[0] if params and isinstance(params[0], (tuple, list)) else params
            shifted = [(x + ox, y + oy) for x, y in raw_pts]
            canvas.poly(shifted, color, filled, sw)
