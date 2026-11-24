#init des module systeme
from machine import Pin

#init des modules
import TEIS_TouchScreen as Touch
import TEIS_Global as Global

#import des vues pour mettre les pointeurs en memoire
import pages.acceuil as acceuil
import pages.recent  as recent
import pages.carteSD as carteSD
import pages.wifi     as wifi
import pages.parametre    as parametre

# pages des paramètres et preférences
import pages.orientation as orientation
import pages.fonts as fonts
import pages.fonts_size as fonts_size
import pages.marge as marge
import pages.themes as themes
import pages.heure as heure

PAGES= {"acceuil":acceuil,
        "recent":recent,
        "carteSD":carteSD,
        "wifi":wifi,
        "parametre":parametre,
            "orientation":orientation,
            "fonts": fonts,
            "fonts_size": fonts_size,
            "marge":marge,
            "themes": themes,
            "date time":heure}

def run():
    import gc
   
    Global.init() #j'initialise tous les modules    
   
    go_page="acceuil"
    page_courante=None
    
    print("mem init: ",gc.mem_free()/1000)
    
    bouton_1 = Pin(21,Pin.IN)
    
    while bouton_1.value(): #tant que j'ai un status de menu
        
        if go_page != page_courante:
            #j'ai changer de vue
            if page_courante is not None:#je regarde si la pages courantes a une fonction exit
                PAGES[page_courante].page_out() #si oui je l'execute, pour par exemple nettoyer l'écran, ou le buffer, ou sauve les paramètres, etc
            page_courante = go_page #je met a jour l'état en pointant vers la page en court
            PAGES[page_courante].page_in() #et je lance la nouvelle pages et du coup je lance menu a l'init
            print("mem: ",gc.mem_free()/1000)
        #je récupère ce que la page me renvoi quand je sort de la boucle de la page
        event_page = PAGES[page_courante].page(Touch.wait_touch(90))
        if event_page in PAGES: #si le nom de retour est une pages existante
            go_page=event_page

#run()
