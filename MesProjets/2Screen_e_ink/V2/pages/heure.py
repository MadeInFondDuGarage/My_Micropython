import myglobal
import mydatetime
import os

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    myglobal.rd.render_draw.draw_rect(0,0,myglobal.rd.WIDTH,myglobal.rd.HEIGHT,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    myglobal.rd.screen.clear()
    
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()
    
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","<b>Thème d'icones</b>",40,1,100)

    #menu paramètres
    taille_police=32
    myglobal.SimpleLigne("<i>choisissez un thème</i>","C",taille_police,4,50)
    myglobal.SimpleLigne("<i>dans la liste ci dessous</i>","C",taille_police,5,50)
    
    #myglobal.screen.show(0,0,270,540)
    
    show_theme((0,0,0), True)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if myglobal.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    show_theme(pos, False)
 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    myglobal.preferences.sauve_prefs() #en sortant je sauvegarde le theme

def sleep():
    #ici je rentre en sommeil, mais je peut aussi activer quelque chose d'autre avant si besoin comme une sauvegarde
    pass

def show_theme(pos, init=True):
    
    liste_theme=os.listdir("themes")
    nbr=len(liste_theme)
    
    if not init: #je suis plus dans l'init
        #myglobal.screen.clean(0,0,960,540,0,0)
        myglobal.screen.clear()#4*75,0,(nbr+1)*75,540)
    
    #je récupère le theme sélectionner
    ligne=myglobal.get_zone_line(pos,75)
    if init or (ligne >= 5 and ligne <=5+nbr): #je suis dans la zone de ma liste de theme
        
        if not init:
            theme_actuel=liste_theme[ligne-5]
            myglobal.preferences.set_pref('theme',theme_actuel)
            myglobal.theme=f"themes/{theme_actuel}"
        theme_actuel=myglobal.preferences.get_pref('theme')
        
        if nbr == 0 :
            myglobal.SimpleLigne("Erreur aucun thème existant","C",45,5,75)
        else:
            for i in range(nbr):
                if theme_actuel==liste_theme[i]:
                    myglobal.SimpleLigne(f"<b>{liste_theme[i]}</b>","C",45,5+i,75)
                else:
                    myglobal.SimpleLigne(liste_theme[i],"C",45,5+i,75)
        
        myglobal.screen.show()#4*75,0,(nbr+1)*75,540)


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

