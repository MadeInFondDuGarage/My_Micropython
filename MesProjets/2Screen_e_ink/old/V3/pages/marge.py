import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime
import TEIS_Clavier_Num as Clavier_Num

modif=False

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    global string_val
        
    Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Marge latéral</b>")  

    #menu paramètres
    taille_police=35
    Render.SimpleLigne("<i>La marge décale le texte</i>","C",taille_police,4,50)
    Render.SimpleLigne("<i>du pourtour de l'écran</i>","C",taille_police,5,50)
  
    marge_actuel=Global.Preferences.get_pref('marge')
    show_marge(marge_actuel, True,False)
    
    #init string clavier
    Clavier_Num.string_clavier=str(marge_actuel)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    global modif
    if Touch.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    if Touch.in_zone_line(pos,430,1): #je rentre dans le mode de modification
        marge_actuel=Global.Preferences.get_pref('marge')
        modif=True
        show_marge(marge_actuel,False,True)
    
    val, string_marge = Clavier_Num.val_clav_num(pos,2)
    
    if val>= -1 and modif==True:
        show_marge(string_marge, False,True)

    if val== -2:#j'ai Ok, je reviens a la normal car j'ai saisie
        modif=False
        Global.Preferences.set_pref('marge',int(string_marge))
        show_marge(string_marge, False,False)


    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    Global.Preferences.sauve_prefs() #en sortant je sauvegarde le theme

def show_marge(marge,init=True,modif_actif=False):
    
    if modif_actif:
        Render.render_draw.draw_rect(170,355,180,100,15,1)
        Render.render_draw.draw_rect(170,355,180,100,0,0)
        Render.set_font_size(30)
        Render.draw_text(f"<i>   ok pour valiser   </i>",0,480,0,15,"C","C")
        Render.set_font_size(80)
        Render.draw_text(f"<b>{marge}</b>",0,400,0,15,"C","C")
        Clavier_Num.show_clav_num(0)
        Render.screen.clear()
        Render.screen.show()
        
    if not modif_actif:
        Render.render_draw.draw_rect(170,355,180,100,15,1) #j'efface le rectangle en écrivant l'inverse
        Render.set_font_size(30)
        Render.draw_text(f"<i>tap pour modifier</i>",0,480,0,15,"C","C")
        Render.set_font_size(80)
        Render.draw_text(f"{marge}",0,400,0,15,"C","C")
        Clavier_Num.show_clav_num(15)
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

