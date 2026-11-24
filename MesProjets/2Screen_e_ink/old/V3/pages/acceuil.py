import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch

def page_in(): #point d'entrée de la page, dédier a la construction du visuel logiquement
    
    Render.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    d,w,h=Render.get_orientation() # je récupère les bonne dimension
    Render.render_draw.draw_rect(0,0,w,h,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    
    #affichage de la datetime ,pc
    Render.DateTime_Pc()
    
    Render.MenuLigne(f"{Global.theme}/Livres ouvert.bmp" ,"Livres en cours",40,2,100)
    Render.MenuLigne(f"{Global.theme}/Parcourir la carte SD.bmp","Parcourir la carte",40,4,100)
    Render.MenuLigne(f"{Global.theme}/Connexion WIFI.bmp","Point Wifi",40,6,100)
    Render.MenuLigne(f"{Global.theme}/Paramètres.bmp","Paramètres",40,8,100)
    
    Render.screen.clear()
    Render.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main

    if Touch.in_zone_line(pos, 2, 100):
        #reader() #j'appel la fonction spécifique a utiliser si besoin
        return "recent"
    
    if Touch.in_zone_line(pos, 4, 100):
        return "carteSD" #je part sur la carte sd

    if Touch.in_zone_line(pos, 6, 100):
        return "wifi" #je part sur la carte sd
    
    if Touch.in_zone_line(pos, 8, 100):
        return "parametre" #mais je peut aussi voir pour lancer une autre page qui ce comporte alors comme un sous menu
        
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    pass
    
if __name__=="__main__":
    
    import time
    from machine import Pin
    import TEIS_Global as Global

    Global.init()
    
    bouton_1 = Pin(21,Pin.IN)
        
    def test():
        page_in()
        while bouton_1.value():
            retour = page(Touch.wait_touch(Render.get_orientation()[0])) #via le render je récupère l'orientation
            print(retour)
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()
