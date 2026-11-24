import myglobal
import mydatetime


def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    myglobal.rd.render_draw.draw_rect(0,0,myglobal.rd.WIDTH,myglobal.rd.HEIGHT,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    myglobal.rd.screen.clear()
    
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()
    
    #Livres en cours
    myglobal.MenuLigne(f"{myglobal.theme}/Parcourir la carte SD.bmp","<i><b>Parcourir la carte SD</b></i>",40,1,100)
    
    myglobal.rd.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    if myglobal.in_zone_line(pos, 1, 100):
        return "acceuil" #je part sur la carte sd

    return None

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
