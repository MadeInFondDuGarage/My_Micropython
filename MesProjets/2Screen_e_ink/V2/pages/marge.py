import myglobal
import mydatetime
import os

string_val=""

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    global string_val
    
    myglobal.rd.render_draw.draw_rect(0,0,myglobal.rd.WIDTH,myglobal.rd.HEIGHT,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    
    myglobal.rd.set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    
    #affichage de la datetime ,pc
    mydatetime.DateTime_Pc()
    
    myglobal.MenuLigne(f"{myglobal.theme}/Paramètres.bmp","<b>Marge latéral</b>",40,1,100)

    #menu paramètres
    taille_police=35
    myglobal.SimpleLigne("<i>La marge décalle le texte</i>","C",taille_police,4,50)
    myglobal.SimpleLigne("<i>du pourtour de l'écran</i>","C",taille_police,5,50)
  
    marge_actuel=myglobal.preferences.get_pref('marge')
    string_val=str(marge_actuel)
    show_marge(string_val, True,False)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    global string_val
    if myglobal.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    if myglobal.in_zone_line(pos,430,1): #je rentre dans le mode de modification
        marge_actuel=myglobal.preferences.get_pref('marge')
        show_marge(marge_actuel,  False,True)
    
    val = myglobal.val_clav_num(pos)
    
    if val>= 0:
        string_val+=str(val)
        string_val=string_val[-2:]
        show_marge(string_val, False,True)
        
    if val==-1:
        string_val=str(int(string_val)//10)
        show_marge(string_val, False,True)

    if val== -2:#j'ai Ok, je reviens a la normal car j'ai saisie
        myglobal.preferences.set_pref('marge',int(string_val))
        show_marge(string_val, False,False)

 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    myglobal.preferences.sauve_prefs() #en sortant je sauvegarde le theme

def sleep():
    #ici je rentre en sommeil, mais je peut aussi activer quelque chose d'autre avant si besoin comme une sauvegarde
    pass

def show_marge(marge,init=True,modif_actif=False):
    
#    if not init: #je suis plus dans l'init
        #myglobal.screen.clean(0,0,960,540,0,0)
#        myglobal.rd.screen.clear()#4*75,0,(nbr+1)*75,540)
    global string_val
    
    if modif_actif:
        myglobal.rd.render_draw.draw_rect(170,355,180,100,15,1)
        myglobal.rd.render_draw.draw_rect(170,355,180,100,0,0)
        myglobal.rd.set_font_size(30)
        myglobal.rd.draw_text(f"<i>   ok pour valiser   </i>",0,480,0,15,"C","C")
        myglobal.rd.set_font_size(80)
        myglobal.rd.draw_text(f"<b>{marge}</b>",0,400,0,15,"C","C")
        myglobal.show_clav_num(0)
        myglobal.rd.screen.clear()
        myglobal.rd.screen.show()
        
    if not modif_actif:
        myglobal.rd.render_draw.draw_rect(170,355,180,100,15,1) #j'efface le rectangle en écrivant l'inverse
        myglobal.rd.set_font_size(30)
        myglobal.rd.draw_text(f"<i>tap pour modifier</i>",0,480,0,15,"C","C")
        myglobal.rd.set_font_size(80)
        myglobal.rd.draw_text(f"{marge}",0,400,0,15,"C","C")
        myglobal.show_clav_num(13)
        myglobal.rd.screen.clear()
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

