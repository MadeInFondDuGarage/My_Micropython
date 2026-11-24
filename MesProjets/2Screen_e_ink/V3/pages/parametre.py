import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime
   
def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Paramètres</b>")
    
    a,mm,j,h, m, s =DateTime.get_time()
    a+=2000
    #menu paramètres
    taille_police=32
    Render.ParamLigne("Orientation",f"<b>{Global.Preferences.get_pref('orientation')}</b>",taille_police,2,100)
    Render.ParamLigne("Fonts",f"<b>{Global.Preferences.get_pref('font_name')}</b>",taille_police,3,100)
    Render.ParamLigne("Taille de la font du lecteur",f"<b>{Global.Preferences.get_pref('font_size')}</b>",taille_police,4,100)
    Render.ParamLigne("Marge latéral",f"<b>{Global.Preferences.get_pref('marge')}</b>",taille_police,5,100)
    Render.ParamLigne("Thème d'icones",f"<b>{Global.Preferences.get_pref('theme')}</b>",taille_police,6,100)
    Render.ParamLigne("Réglage de la date",f"<b>{j:02}/{mm:02}/{a:04}</b>",taille_police,7,100)
    Render.ParamLigne("Réglage de l'heure",f"<b>{h:02}:{m:02}</b>",taille_police,8,100)

    Render.screen.clear()
    Render.screen.show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if Touch.in_zone_line(pos, 1, 100):
        return "acceuil" #je retourne a l'acceuil
    
    if Touch.in_zone_line(pos,2,100,50):
        return "orientation" 

    if Touch.in_zone_line(pos,3,100,50):
        return "fonts" 
    
    if Touch.in_zone_line(pos,4,100,50):
        return "fonts_size"
    
    if Touch.in_zone_line(pos,5,100,50):
        return "marge"
    
    if Touch.in_zone_line(pos,6,100,50):
        return "themes"
    
    if Touch.in_zone_line(pos,7,100,50):
        return "date time"
    
    if Touch.in_zone_line(pos,8,100,50):
        return "date time" 
 
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
            retour = page(Touch.wait_touch(90))
            print(retour)
            time.sleep_ms(200)
        page_out()
        print("fin")
    
    test()
