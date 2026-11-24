from machine import lightsleep
import ctx
import settings

import views.menu     as menu
import views.library  as library
import views.explorer as explorer
import views.wifi     as wifi
import views.prefs    as prefs

VIEWS = {
    "menu":     menu,
    "library":  library,
    "explorer": explorer,
    "wifi":     wifi,
    "prefs":    prefs,
}

def run():
    ctx.init()
    ctx.push("menu")
    current = None

    while ctx.stack:
        state = ctx.stack[-1]

        if state != current:
            if current and VIEWS[current].ACTIVITY.get("exit"):
                VIEWS[current].ACTIVITY["exit"]()
            current = state
            VIEWS[current].ACTIVITY["enter"]()

        if ctx.touch_event:
            next_state = VIEWS[current].ACTIVITY["update"]()
            if next_state == "back":
                ctx.pop()
                current = None
            elif next_state is False:
                break
            elif next_state in VIEWS:
                ctx.push(next_state)
                current = None
        elif VIEWS[current].ACTIVITY.get("sleep", True):
            lightsleep()

run()
