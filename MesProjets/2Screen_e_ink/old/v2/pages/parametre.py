import myglobal
import mydatetime

#@myglobal.mesure_time("charge")
def charge():
    myglobal.rd.screen.clean(0,0,960,540,0,1) #j'efface l'ecran et le buffer
    myglobal.rd.screen.clear()
    
    #entete
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()

#@myglobal.mesure_time("show")
def show():
    myglobal.screen.show()
    
#@myglobal.mesure_time("param_in")
def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    
    charge()
    
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","<b>Paramètres</b>",40,1,100)
    
    a,mm,j,h, m, s =myglobal.i2c_rtc.get_time()
    a+=2000
    #menu paramètres
    taille_police=32
    myglobal.ParamLigne("Orientation",f"<b>{myglobal.preferences.get_pref('orientation')}</b>",taille_police,3,75)
    myglobal.ParamLigne("Fonts",f"<b>{myglobal.preferences.get_pref('font_name')}</b>",taille_police,4,75)
    myglobal.ParamLigne("Taille de la font du lecteur",f"<b>{myglobal.preferences.get_pref('font_size')}</b>",taille_police,5,75)
    myglobal.ParamLigne("Marge latéral",f"<b>{myglobal.preferences.get_pref('marge')}</b>",taille_police,6,75)
    myglobal.ParamLigne("Thème d'icones",f"<b>{myglobal.preferences.get_pref('theme')}</b>",taille_police,7,75)
    myglobal.ParamLigne("Réglage de la date",f"<b>{j:02}/{mm:02}/{a:04}</b>",taille_police,8,75)
    myglobal.ParamLigne("Réglage de l'heure",f"<b>{h:02}:{m:02}</b>",taille_police,9,75)

    show()

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if myglobal.in_zone_line(pos, 1, 100):
        return "acceuil" #je retourne a l'acceuil
    
    if myglobal.in_zone_line(pos,3,75,50):
        return "orientation" 

    if myglobal.in_zone_line(pos,4,75,50):
        return "fonts" 
    
    if myglobal.in_zone_line(pos,5,75,50):
        return "fonts"
    
    if myglobal.in_zone_line(pos,6,75,50):
        return "marge"
    
    if myglobal.in_zone_line(pos,7,75,50):
        return "themes"
    
    if myglobal.in_zone_line(pos,8,75,50):
        return "date"
    
    if myglobal.in_zone_line(pos,9,75,50):
        return "heure" 
 
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
