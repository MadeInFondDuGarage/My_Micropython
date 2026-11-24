import ctx
import preferences
from machine import lightsleep

# zones de touch (x1, y1, x2, y2)
_ZONE_LIRE  = (20,  100, 540, 350)
_ZONE_RETOUR  = (20,  400, 540, 600)
_ZONE_WIFI  = (20,  400, 540, 600)

def _in_zone(x, y, zone):
    return zone[0] <= x <= zone[2] and zone[1] <= y <= zone[3]

def in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    r = ctx.render
    ctx.screen.clear()
    ctx.screen.show()

def page(): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    x, y = ctx.touch_event #j'ai récupérer l'évenment du touch
    ctx.touch_event = None #je le remet a zéro
    
    #exemple ici je suis dans la zone ou j'ai appuyer sur dernier livres
    if _in_zone(x, y, _ZONE_RETOUR):
        return "retour" #je sort et je reviend au menu d'avant

    if _in_zone(x, y, _ZONE_LIRE):
        reader() #j'appel la fonction spécifique a utiliser

    if _in_zone(x, y, _ZONE_WIFI):
            return "wifi" #mais je peut aussi voir pour lancer une autre page qui ce comporte alors comme un sous menu

    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def out():#pour la partie sorti de la page en cours
    pass

def sleep():
    #ici je rentre en sommeil, mais je peut aussi activer quelque chose d'autre avant si besoin comme une sauvegarde
    lightsleep()
    
    
ACTIVITY = {
    "in":  in,
    "page": page,
    "out":   out,
    "sleep":  sleep,
    }
