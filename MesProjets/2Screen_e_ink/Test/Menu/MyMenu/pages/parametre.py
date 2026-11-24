import myglobal

# zones de touch (x1, y1, x2, y2)
_ZONE_ACCUEIL  = (20,  100, 540, 200)

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    myglobal.screen.clean(0,0,960,540,0,1) #j'efface l'ecran et le buffer
    myglobal.screen.clear()
       
    myglobal.render.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter    
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","<b>Paramètres</b>",40,1,100)
    
    myglobal.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if myglobal.in_zone(pos, _ZONE_ACCUEIL):
        return "acceuil" #je part sur la carte sd
 
 
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
            n, points = myglobal.touch.read_points()
            if n>0:
                x, y = myglobal.HwOrientation(points[0][0], points[0][1]) 
                retour = page(x,y)
                print(retour)
            if not myglobal.bouton_1.value():
                break
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()
