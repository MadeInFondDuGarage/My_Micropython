import ctx
import settings

# zones de touch (x1, y1, x2, y2)
_ZONE_LAST_BOOK  = (20,  100, 540, 350)
_ZONE_EXPLORER   = (20,  400, 540, 600)
_ZONE_PREFS      = (20,  650, 540, 800)

def _in_zone(x, y, zone):
    return zone[0] <= x <= zone[2] and zone[1] <= y <= zone[3]

def _enter():
    r = ctx.render
    r.clear()

    r.set_font("HersheySansMed.bin")
    r.set_font_size(28)
    r.set_text("Accueil")
    r.draw_text(280, 40, 0, 28, "C", "C")

    # dernier livre
    r.set_font_size(22)
    r.set_text("Dernier livre")
    r.draw_text(40, 120, 0, 22, "L", "C")

    last = settings.get("last_book")
    title = last if last else "Aucun livre"
    r.set_font_size(32)
    r.set_text(title)
    r.draw_text(40, 180, 0, 32, "L", "C")

    # explorer
    r.set_font_size(32)
    r.set_text("Explorer la carte SD")
    r.draw_text(40, 480, 0, 32, "L", "C")

    # préférences
    r.set_font_size(32)
    r.set_text("Préférences")
    r.draw_text(40, 720, 0, 32, "L", "C")

    ctx.display.show()

def _update():
    x, y = ctx.touch_event
    ctx.touch_event = None

    if _in_zone(x, y, _ZONE_LAST_BOOK) and settings.get("last_book"):
        return "reader"
    if _in_zone(x, y, _ZONE_EXPLORER):
        return "explorer"
    if _in_zone(x, y, _ZONE_PREFS):
        return "prefs"

    return None

ACTIVITY = {
    "enter":  _enter,
    "update": _update,
    "exit":   None,
    "sleep":  True,
}
