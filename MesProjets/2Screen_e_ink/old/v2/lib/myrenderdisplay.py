import t547
import render_image_4bpp as render_image
import render_draw_4bpp as render_draw
import render_glyph_4bpp as render_glyph

HELP="""Moteur de rendu pour fonte de type Hershey qui vs avec les extensions inkscape 
            init: buffer externe, largeur du buffer, hauteur du buffer (init du module et infos de l'écran) 
            set_font : font (memory view ou .py des fonts) 
            set_orientation : 0,90,180,270. (représente les orientations du rendu dans le buffer) 
            draw_pixel: x,y,couleur ( ecris un pixel dans le buffer, couleur de 0 a 15, 15 = blanc 0 = noir)
            draw_line: x1,y1,x2,y2,couleur (ecris une ligne dans le buffer couleur comme le pixel)
            set_bmp: passe le chemin/nom de l'image sous forme de chaine
            set_text: chaine du texte a écrire
            set_font_size: taille du rendu de la font en pixel de haut 
            set_titre: de 0 a 6, pour adapter la taille de la font proportionnelement au choix initial de la taille de la font
            draw_text:x,y,couleur font, couleur de fond, justif, centre. (dessine le texte a la position demder, avec la couleur 0 a 255. la couleur de fond est de -1 (aucune nettoyage du buffer), 0 a 255)
                justif:"L","G","C","D" justification libre, gauche, centre et droite sur lécran. avec D,C,G le x n'est pas pris en compte. on est toujours avec un x=5
                centre:"B","C","H" position du texte par rapport a x.  
            get_zone: renvoie x,y,largeur,hauteur de la zone qui est occuper par le texte. permet de nettoyer l'écran avant sur des eink
            draw_bmp:x,y,eclaircir (x et y position relative et eclaircir est comprie en 0 et 2, si inférieur a 0 cela assombri, au dessus eclaircir, 1.2 marche bien
            """
FONT_UNITS_HEIGHT = 120   # hauteur logique normalisée (TARGET_RANGE)
FONT_SPACE = 10           # espace par défaut si glyph absent
ORIENTATION=0
FONT_SIZE=30
TITRE=1
JUSTIF="G" #postion latéral en X
CENTRE="B" #centrage du texte par défaut lier au bas. si je met 0 en y quelque soit la taille du texte on le vois parraitre
BmpWIDTH  = None #largeur
BmpHEIGHT = None #hauteur
BmpBPP = None

#j'instancie la gestion de l'écran
screen = t547.T547()
screen.init()

buf,HwWIDTH,HwHEIGHT = screen.get_buffer(), screen.width(), screen.height()

#j'init le render d'écran
render_draw.set_context(buf, HwWIDTH, HwHEIGHT)
render_glyph.set_context(buf, HwWIDTH, HwHEIGHT)

ORIENTATION=90
render_draw.set_orientation(ORIENTATION)
render_glyph.set_orientation(ORIENTATION)


def set_font(font_module):
    # on ouvre un FICHIER binaire
    render_glyph.set_font(font_module)
        
# ---------- Chargement ----------
def set_bmp(fichier):
    BmpWIDTH, BmpHEIGHT, BmpBPP = render_image.bmp_load(fichier)
            
# -----------Rotate ---------
def set_orientation(deg):
    #definie l'orientation de l'écriture des polices sur l'écran
    if deg > -1 and deg < 90:
        deg=0
        WIDTH=HwWIDTH
        HEIGHT=HwHEIGHT
    elif deg > 89 and deg <180 :
        deg= 90
        WIDTH=HwHEIGHT
        HEIGHT=HwWIDTH
    elif deg > 179 and deg < 269:
        deg=180
        WIDTH=HwWIDTH
        HEIGHT=HwHEIGHT
    elif deg > 269 and deg < 360:
        deg = 270
        WIDTH=HwHEIGHT
        HEIGHT=HwWIDTH
    else:
        deg=0
        WIDTH=HwWIDTH
        HEIGHT=HwHEIGHT
    
    render_draw.set_orientation(deg)
    render_glyph.set_orientation(deg)
    ORIENTATION=deg

def get_orientation():
    return render_draw.get_orientation()

def get_HwOrientation(phyX,phyY):
    #transforme les entré physique vers les valeurs logique pour relier avec la position des menu
    x=phyX
    y=phyY
    deg,W,H=render_draw.get_orientation()
    
    if deg==0:
        x=phyX
        y=H - 1 - phyY
    
    elif deg== 90:
        y= phyX
        x= phyY
        
    elif deg == 180:
        x = W - 1 - phyX
        y = phyY
        
    elif deg ==270:
        x = W - 1 - phyY
        y = H - 1 - phyX
        
    return x,y

# ---------- Pixel ----------
def draw_pixel(x, y, color):
    render_draw.draw_pixel(x, y, color)

# ---------- Ligne ----------
def draw_line( x1, y1, x2, y2, color):
    #dessine une ligne dans le buffer
    render_draw.draw_line(x1, y1, x2, y2, color)
            
        
def set_font_size(font_size_px):
    #definition de la taille de la police
    render_glyph.set_font_size(font_size_px)
        
def set_titre(titre):
    #définition de la taille des titre pour faire l'équivalent des h1 a h6
    render_glyph.set_titre(titre)
        
def draw_text(text, x, y, color, backcolor=-1,justif="L",centre="H"):
    # je met le backcolor a -1 par défaut car pas forcement nécéssaire et -1 enlever le remplissage du buffer
    h=v=0
    #je repasse la valeur de l'orientation dans le filtre au cas ou on ait passer en direct
    if justif!="L":
        if justif=="G":
            h=1
        elif justif=="D":
            h=2
        elif justif=="C":
            h=3
        else:
            h=0
            
    if centre=="H":
        v=0
    elif centre=="C":
        v=1
    else:
        v=2
    
    render_glyph.draw_text(text,x,y,color,backcolor,h,v)
  
    
def draw_bmp(x, y, centre="H"):
    set_orientation(ORIENTATION)
    if centre == "H":
        decallage = 0
    elif centre == "C":
        decallage = BmpHEIGHT // 2
    else:
        decallage = BmpHEIGHT
    render_image.bmp_draw(BUF, HwWIDTH, HwHEIGHT,
                          ORIENTATION, x, y, decallage)
                
   
def get_zone(self):
    #récupère la zone/surface ou sera écrit le texte. pemet de nettoyer avant ou de colorer, ou de dessiner autour
    #format x,y,largeur,hauteur
    return render_glyph.get_zone()
        
        
                
            



