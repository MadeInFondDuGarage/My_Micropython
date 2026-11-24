import myglobal
import mydatetime

@myglobal.mesure_time("param_in")
def page_in(): #point d'entrée de la page, dédier a la construction du visuel logiquement
    
    myglobal.rd.render_draw.draw_rect(0,0,myglobal.rd.WIDTH,myglobal.rd.HEIGHT,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    myglobal.rd.screen.clear()
    
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()
    
    print(myglobal.theme)
    myglobal.MenuLigne(f"{myglobal.theme}/Livres ouvert.bmp" ,"Livres en cours",40,2,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Parcourir la carte SD.bmp","Parcourir la carte",40,4,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Connexion WIFI.bmp","Point Wifi",40,6,100)
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","Paramètres",40,8,100)
    
    myglobal.rd.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main

    if myglobal.in_zone_line(pos, 2, 100):
        #reader() #j'appel la fonction spécifique a utiliser si besoin
        return "recent"
    
    if myglobal.in_zone_line(pos, 4, 100):
        return "carteSD" #je part sur la carte sd

    if myglobal.in_zone_line(pos, 6, 100):
        return "wifi" #je part sur la carte sd
    
    if myglobal.in_zone_line(pos, 8, 100):
        return "parametre" #mais je peut aussi voir pour lancer une autre page qui ce comporte alors comme un sous menu
        
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
        while myglobal.bouton_1.value():
            retour = page(myglobal.wait_touch())
            print(retour)
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()
