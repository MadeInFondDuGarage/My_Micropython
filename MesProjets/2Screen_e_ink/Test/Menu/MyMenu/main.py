import myglobal

#import des vues pour mettre les pointeurs en memoire
import pages.acceuil as acceuil
import pages.recent  as recent
import pages.carteSD as carteSD
import pages.wifi     as wifi
import pages.parametre    as parametre

PAGES= {"acceuil":acceuil,"recent":recent,"carteSD":carteSD, "wifi":wifi,"prefs":parametre}

def run():
    #je charge les préférence utilisateurs
    myglobal.preferences.charge_prefs()
    
    go_page="acceuil"
    page_courante=None
    
    while myglobal.bouton_1.value(): #tant que j'ai un status de menu
        
        if go_page != page_courante:
            #j'ai changer de vue
            if page_courante is not None:#je regarde si la pages courantes a une fonction exit
                PAGES[page_courante].page_out() #si oui je l'execute, pour par exemple nettoyer l'écran, ou le buffer, ou sauve les paramètres, etc
            page_courante = go_page #je met a jour l'état en pointant vers la page en court
            PAGES[page_courante].page_in() #et je lance la nouvelle pages et du coup je lance menu a l'init
        
        #je récupère ce que la page me renvoi quand je sort de la boucle de la page
        event_page = PAGES[page_courante].page(myglobal.wait_touch())
        
        if event_page in PAGES: #si le nom de retour est une pages existante
            go_page=event_page

        #si j'ai une action de type sleep de prévue ou pas.
#        elif PAGES[page_courante].ACTIVITY.get("sleep"):
#            PAGES[page_courante].sleep() #je lance la fonction pour le sleep           

#run()
