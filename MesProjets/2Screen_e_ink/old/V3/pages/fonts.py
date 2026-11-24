import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime
import os

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>fonts du lecteur</b>")

    #menu paramètres
    taille_police=32
    Render.SimpleLigne("<i>choisissez une font</i>","C",taille_police,4,50)
    Render.SimpleLigne("<i>dans la liste ci dessous</i>","C",taille_police,5,50)
    
    show_fonts((0,0,0), True)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if Touch.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    show_fonts(pos, False)
 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    Global.Preferences.sauve_prefs() #en sortant je sauvegarde le theme
    Render.set_font(Global.sys_font)

def show_fonts(pos, init=True):
    
    liste_fonts=os.listdir("fonts")
    nbr=len(liste_fonts)
      
    #je récupère le theme sélectionner
    ligne=Touch.get_zone_line(pos,80)
    if init or (ligne >= 5 and ligne <=5+nbr): #je suis dans la zone de ma liste de theme
        
        
        if not init:#je sauvegarde si je viens de modifier la font
            font_actuel=liste_fonts[ligne-5]
            Global.Preferences.set_pref('font_name',font_actuel)
            Global.font_name=f"fonts/{font_actuel}"
        font_actuel=Global.Preferences.get_pref('font_name')
        
        if nbr == 0 :
             #je remet la font systeme
            Render.set_font(Global.sys_font)
            Render.SimpleLigne("Erreur aucun fonts trouvées","C",45,5,75)
        else:
            for i in range(nbr):
                Render.set_font(f"fonts/{liste_fonts[i]}")
                Render.SimpleLigne("Une belle journée d'été","C",45,5+i,80)
                if font_actuel==liste_fonts[i]:
                    x,y,w,h=Render.get_zone()
                    Render.render_draw.draw_rect(x,y,w,h,0,0)
                             
        Render.screen.clear()
        Render.screen.show()


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

