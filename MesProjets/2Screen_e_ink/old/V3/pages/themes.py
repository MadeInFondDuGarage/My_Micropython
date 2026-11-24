import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime
import os

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Thème d'icones</b>")
    
    #menu paramètres
    taille_police=32
    Render.SimpleLigne("<i>choisissez un thème</i>","C",taille_police,4,50)
    Render.SimpleLigne("<i>dans la liste ci dessous</i>","C",taille_police,5,50)
    
    show_theme((0,0,0), True)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if Touch.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    show_theme(pos, False)
 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    Global.Preferences.sauve_prefs() #en sortant je sauvegarde le theme

def show_theme(pos, init=True):
    
    liste_theme=os.listdir("themes")
    nbr=len(liste_theme)
      
    #je récupère le theme sélectionner
    ligne=Touch.get_zone_line(pos,75)
    if init or (ligne >= 5 and ligne <=5+nbr): #je suis dans la zone de ma liste de theme
        
        if not init:
            theme_actuel=liste_theme[ligne-5]
            Global.Preferences.set_pref('theme',theme_actuel)
            Global.theme=f"themes/{theme_actuel}"
        theme_actuel=Global.Preferences.get_pref('theme')
        
        Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Thème d'icones</b>")#je l'affiche en début car il éfface le buffer
        
        if nbr == 0 :
            Render.SimpleLigne("Erreur aucun thème existant","C",45,5,75)
        else:
            for i in range(nbr):
                Render.SimpleLigne(liste_theme[i],"C",45,5+i,75)
                if theme_actuel==liste_theme[i]:
                    x,y,w,h=Render.get_zone()
                    Render.render_draw.draw_rect(x,y,w,h,0,0)

        
        

        #menu paramètres
        taille_police=32
        Render.SimpleLigne("<i>choisissez un thème</i>","C",taille_police,4,50)
        Render.SimpleLigne("<i>dans la liste ci dessous</i>","C",taille_police,5,50)
        
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

