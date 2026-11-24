import TEIS_Global as Global
import TEIS_Render as Render
import TEIS_TouchScreen as Touch
import TEIS_DateTimePc as DateTime
import TEIS_Clavier_Num as Clavier_Num

modif=0
annee,mois,jours,heures, minutes, seconds =0,0,0,0,0,0

def page_in(): #point d'entré de la page, dédier a la construction du visuel logiquement
    
    global annee,mois,jours,heures, minutes, seconds
    Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Date Heure</b>")
    
    annee,mois,jours,heures, minutes, seconds=DateTime.get_time()
    
    show_time(annee,mois,jours,heures,minutes,0)
    #init string clavier
    Clavier_Num.string_clavier=str(0)

def page(pos): #ici on a logiquement l'action principal qui peut être une boucle ou pas mais on renvoie un éléments a la boule de base sinon dans le main
    #Page est une boucle mais qui est gérer en repassant dans le main. 
    global modif
    global annee,mois,jours,heures, minutes, seconds
    
    if Touch.in_zone_line(pos, 1, 100):
        return "parametre" #je retourne sur les paramètres généraux
    
    if Touch.in_zone_line(pos,430,1): #je rentre dans le mode de modification
        #test pour voir si j'ai l'heure ou les minutes de sélectionner
        WIDTH=Render.get_orientation()[1]/4
        if Touch.in_zone_col(pos,2,WIDTH,WIDTH):
            modif=1 #pour l'heure par defaut
            Clavier_Num.string_clavier=str(heures)
        if Touch.in_zone_col(pos,3,WIDTH,WIDTH):
            modif=2 #pour l'heure par defaut
            Clavier_Num.string_clavier=str(minutes)
        show_time(annee,mois,jours,heures,minutes,modif)
    
    if Touch.in_zone_line(pos,330,1): #je rentre dans le mode de modification
        #test pour voir si j'ai l'heure ou les minutes de sélectionner
        WIDTH=Render.get_orientation()[1]/4
        if Touch.in_zone_col(pos,1,WIDTH,WIDTH):
            modif=3 #pour l'heure par defaut
            Clavier_Num.string_clavier=str(jours)
        if Touch.in_zone_col(pos,2,WIDTH,WIDTH):
            modif=4 #pour l'heure par defaut
            Clavier_Num.string_clavier=str(mois)
        if Touch.in_zone_col(pos,3,WIDTH,WIDTH) or Touch.in_zone_col(pos,4,WIDTH,WIDTH):
            modif=5 #pour l'heure par defaut
            Clavier_Num.string_clavier=str(annee)
        show_time(annee,mois,jours,heures,minutes,modif)
        
    val, stringval = Clavier_Num.val_clav_num(pos,2)
    
    if val>= -1 and modif!=0: #ici j'ai eu un appui touche
        if modif==1:
            if int(stringval) < 24:
                heures=int(stringval)
        if modif==2:
            if int(stringval) <60:
                minutes=int(stringval)
        if modif==3:
            if int(stringval) <32:
                jours=int(stringval)
        if modif==4:
            if int(stringval) <13:
                mois=int(stringval)
        if modif==5:
            if int(stringval) <60:
                annee=int(stringval)

                               
        show_time(annee,mois,jours,heures,minutes,modif)


    if val== -2:#j'ai Ok, je reviens a la normal car j'ai saisie
        DateTime.set_time(annee,mois,jours,heures, minutes, seconds)
        modif=0
        Render.PageEntete(f"{Global.theme}/Paramètres.bmp","<b>Date Heure</b>") 
        show_time(annee,mois,jours,heures,minutes,modif)
     
        
    
 
    return None #sinon je renvoie rien. je repasse ici que si le main.py vois a nouveau une action sur le touch.

def page_out():#pour la partie sorti de la page en cours
    None

def show_time(annee,moi,jours,heures,minutes,modif_actif=0):
    annee+=2000
    font_name=Global.Preferences.get_pref('font_name')
    Render.set_font(f"fonts/{font_name}")
    Render.set_font_size(40)
    Render.render_draw.draw_rect(0,170,540,200,15,1) #on efface le buffer sur la zone
        
    if modif_actif !=0:
        Render.set_font_size(30)
        Render.draw_text(f"<i>   ok pour valider   </i>",0,480,0,15,"C","C")
        Render.set_font_size(75)
        if modif_actif==1: #si j'ai l'heure de selectionner
            Render.draw_text(f"{jours:02} {mois:02} {annee:04}",0,300,0,15,"C","C")
            Render.draw_text(f"<b>{heures:02}</b>:{minutes:02}",0,400,0,15,"C","C")
        if modif_actif==2:#sinon c'est les minutes
            Render.draw_text(f"{jours:02} {mois:02} {annee:04}",0,300,0,15,"C","C")
            Render.draw_text(f"{heures:02}:<b>{minutes:02}</b>",0,400,0,15,"C","C")
        if modif_actif==3:#jours
            Render.draw_text(f"<b>{jours:02}</b> {mois:02} {annee:04}",0,300,0,15,"C","C")
            Render.draw_text(f"{heures:02}:{minutes:02}",0,400,0,15,"C","C")
        if modif_actif==4:#mois
            Render.draw_text(f"{jours:02} <b>{mois:02}</b> {annee:04}",0,300,0,15,"C","C")
            Render.draw_text(f"{heures:02}:{minutes:02}",0,400,0,15,"C","C")
        if modif_actif==5:#annee
            Render.draw_text(f"{jours:02} {mois:02} <b>{annee:04}</b>",0,300,0,15,"C","C")
            Render.draw_text(f"{heures:02}:{minutes:02}",0,400,0,15,"C","C")
        Clavier_Num.show_clav_num(0) #on affiche le clavier

    else:
        Render.set_font_size(75)
        Render.draw_text(f"{jours:02} {mois:02} {annee:04}",0,300,0,15,"C","C")
        Render.draw_text(f"{heures:02}:{minutes:02}",0,400,0,15,"C","C")
        Render.set_font_size(30)
        Render.draw_text(f"<i>tap pour modifier</i>",0,480,0,15,"C","C")

        Clavier_Num.show_clav_num(15) #j'efface le clavier en imprimant l'inverse sur le buffer
        
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

