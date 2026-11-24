import myglobal

# zones de touch (x1, y1, x2, y2)
_ZONE_LIRE  = (20,  50, 500, 350)
_ZONE_CARTE  = (20,  350, 500, 550)
_ZONE_WIFI  = (20,  550, 500, 750)
_ZONE_PARAM  = (20,  750, 500, 950)

def page_in(): #point d'entrée de la page, dédier a la construction du visuel logiquement
    
    myglobal.screen.clean(0,0,960,540,0,1) #j'efface l'ecran et le buffer
    myglobal.screen.clear()
    
    myglobal.render.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    myglobal.MenuLigne(f"{myglobal.theme}/Livres ouvert.bmp" ,"Livres en cours",40,2,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Parcourir la carte SD.bmp","Parcourir la carte",40,4,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Connexion WIFI.bmp","Point Wifi",40,6,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","Paramètres",40,8,100)

    myglobal.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main

    if myglobal.in_zone(pos, _ZONE_LIRE):
        #reader() #j'appel la fonction spécifique a utiliser si besoin
        return "recent"
        #reader() #j'appel la fonction spécifique a utiliser si besoin
    
    if myglobal.in_zone(pos, _ZONE_CARTE):
        return "carteSD" #je part sur la carte sd

    if myglobal.in_zone(pos, _ZONE_WIFI):
        return "wifi" #je part sur la carte sd
    
    if myglobal.in_zone(pos, _ZONE_PARAM):
        return "prefs" #mais je peut aussi voir pour lancer une autre page qui ce comporte alors comme un sous menu
        
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    pass

def sleep():
    #ici je rentre en sommeil, mais je peut aussi activer quelque chose d'autre avant si besoin comme une sauvegarde
    pass
    
if __name__=="__main__":
    
    import time
    def test():
        page_in()
        while 1:
            if myglobal.touch.irq:
                retour = page()
                print(retour)
            if not myglobal.bouton_1.value():
                break
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()
