import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
       
    Render.PageEntete(f"{Global.theme}/Connexion WIFI.bmp","<b>Point Wifi</b>")
    
    Render.screen.clear()
    Render.screen.show() 

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    if Touch.in_zone_line(pos, 1, 100):
        return "acceuil" #je part sur la carte sd
   
    return None

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
            retour = page(Touch.wait_touch(90))
            print(retour)
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()

