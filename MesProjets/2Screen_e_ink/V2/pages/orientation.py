import myglobal
import mydatetime
import os

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    myglobal.rd.render_draw.draw_rect(0,0,myglobal.rd.WIDTH,myglobal.rd.HEIGHT,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    myglobal.rd.screen.clear()
    
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()
    
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","<b>Orientation</b>",40,1,100)

    #menu paramètres
    taille_police=32
    myglobal.SimpleLigne("<i>choisissez une orientation</i>","C",taille_police,4,50)
    myglobal.SimpleLigne("<i>valable pour la lecture</i>","C",taille_police,5,50)
    
    #myglobal.screen.show(0,0,270,540)
    show_orientation((0,0,0), True)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    if myglobal.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    change=False # un chagement
    hauteur=350
    ecart=50
    
    if myglobal.in_zone_line(pos,hauteur+40,1,80):
        orientation_actuel= 90
        change=True

    if myglobal.in_zone_line(pos,hauteur+120+ecart+50,1,100):
        orientation_actuel= 0
        change=True
    
    if myglobal.in_zone_line(pos,hauteur+120+78+40+2*ecart,1,80):
        orientation_actuel= 180
        change=True
    
    if myglobal.in_zone_line(pos,hauteur+2*120+78+50+3*ecart,1,100):
        orientation_actuel= 270
        change=True
    
    if change==True:
        myglobal.preferences.set_pref('orientation',orientation_actuel)
        show_orientation(pos, False)
 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    myglobal.preferences.sauve_prefs() #en sortant je sauvegarde le paramètre

def sleep():
    #ici je rentre en sommeil, mais je peut aussi activer quelque chose d'autre avant si besoin comme une sauvegarde
    pass

def show_orientation(pos, init=True):
    
    if not init: #je suis plus dans l'init
        #myglobal.screen.clean(0,0,960,540,0,0)
        myglobal.rd.screen.clear()#4*75,0,(nbr+1)*75,540)
        
    #commme j'écrit au même endroit je n'efface pas avant
    orientation_actuel=myglobal.preferences.get_pref('orientation')

    centre=250
    hauteur=350
    ecart=50
    selected=0
    not_selected=13
    select=0
    
    if orientation_actuel==90:
        select=selected
    else:
        select=not_selected
    i=centre-78//2
    j=hauteur
    myglobal.rd.render_draw.draw_rect(0+i,0+j,78,120,select,1)
    myglobal.rd.render_draw.draw_rect(4+i,4+j,70,100,15,1)
    myglobal.rd.render_draw.draw_circle(13+i,13+j,5,select,1)
    myglobal.rd.render_draw.draw_line(13+i,13+j,65+i,13+j,select)
    myglobal.rd.render_draw.draw_line(13+i,23+j,65+i,23+j,select)
    myglobal.rd.render_draw.draw_line(13+i,33+j,65+i,33+j,select)
    myglobal.rd.render_draw.draw_line(13+i,43+j,65+i,43+j,select)
    myglobal.rd.render_draw.draw_line(13+i,53+j,40+i,53+j,select)

    if orientation_actuel==0:
        select=selected
    else:
        select=not_selected
    i=centre-120//2
    j=hauteur+120+ecart
    myglobal.rd.render_draw.draw_rect(0+i,0+j,120,78,select,1)
    myglobal.rd.render_draw.draw_rect(4+i,4+j,100,70,15,1)
    myglobal.rd.render_draw.draw_circle(13+i,13+j,5,select,1)
    myglobal.rd.render_draw.draw_line(13+i,13+j,80+i,13+j,select)
    myglobal.rd.render_draw.draw_line(13+i,23+j,80+i,23+j,select)
    myglobal.rd.render_draw.draw_line(13+i,33+j,80+i,33+j,select)
    myglobal.rd.render_draw.draw_line(13+i,43+j,80+i,43+j,select)
    myglobal.rd.render_draw.draw_line(13+i,53+j,60+i,53+j,select)

    if orientation_actuel==180:
        select=selected
    else:
        select=not_selected
    i=centre-78//2
    j=hauteur+120+78+2*ecart
    myglobal.rd.render_draw.draw_rect(0+i,0+j,78,120,select,1)
    myglobal.rd.render_draw.draw_rect(4+i,16+j,70,100,15,1)
    myglobal.rd.render_draw.draw_circle(13+i,23+j,5,select,1)
    myglobal.rd.render_draw.draw_line(13+i,26+j,65+i,26+j,select)
    myglobal.rd.render_draw.draw_line(13+i,36+j,65+i,36+j,select)
    myglobal.rd.render_draw.draw_line(13+i,46+j,65+i,46+j,select)
    myglobal.rd.render_draw.draw_line(13+i,56+j,65+i,56+j,select)
    myglobal.rd.render_draw.draw_line(13+i,66+j,40+i,66+j,select)

    if orientation_actuel==270:
        select=selected
    else:
        select=not_selected
    i=centre - 120//2
    j=hauteur+2*120+78+3*ecart
    myglobal.rd.render_draw.draw_rect(0+i,0+j,120,78,select,1)
    myglobal.rd.render_draw.draw_rect(16+i,4+j,100,70,15,1)
    myglobal.rd.render_draw.draw_circle(33+i,13+j,5,select,1)
    myglobal.rd.render_draw.draw_line(33+i,13+j,95+i,13+j,select)
    myglobal.rd.render_draw.draw_line(33+i,23+j,95+i,23+j,select)
    myglobal.rd.render_draw.draw_line(33+i,33+j,95+i,33+j,select)
    myglobal.rd.render_draw.draw_line(33+i,43+j,95+i,43+j,select)
    myglobal.rd.render_draw.draw_line(33+i,53+j,80+i,53+j,select)
    
    myglobal.rd.screen.show()



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

