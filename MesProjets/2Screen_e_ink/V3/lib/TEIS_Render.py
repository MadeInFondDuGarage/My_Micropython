"""
    Ce module rassemble les éléments de rendu aggréger pour la carte lyligo
"""

import t547
import render_image_4bpp as render_image
import render_draw_4bpp as render_draw
import render_glyph_4bpp as render_glyph
import TEIS_DateTimePc as dt
import micropython


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
FONT_SIZE=30
TITRE=1
JUSTIF="G" #postion latéral en X
CENTRE="B" #centrage du texte par défaut lier au bas. si je met 0 en y quelque soit la taille du texte on le vois parraitre
WIDTH=None
HEIGHT=None

screen=None

def init_screen():
    #j'instancie la gestion de l'écran
    global screen
    
    screen = t547.T547()
    screen.init()

    BUF,HwWIDTH,HwHEIGHT = screen.get_buffer(), screen.width(), screen.height()

    #j'init le render d'écran
    render_draw.set_context(BUF, HwWIDTH, HwHEIGHT)
    render_glyph.set_context(BUF, HwWIDTH, HwHEIGHT)
    render_image.set_context(BUF, HwWIDTH, HwHEIGHT)
    
    set_orientation(90)

def set_font(font_module):
    # on ouvre un FICHIER binaire
    render_glyph.set_font(font_module)
            
# -----------Rotate ---------
def set_orientation(deg):
    #definie l'orientation de l'écriture des polices sur l'écran*
    render_draw.set_orientation(deg)
    render_glyph.set_orientation(deg)
    render_image.set_orientation(deg)
    
def get_orientation():
    return render_draw.get_orientation()

def get_HwOrientation(phyX,phyY,hwW,hwH):
    #transforme les entré physique vers les valeurs logique pour relier avec la position des menu
    x=phyX
    y=phyY
    deg,W,H=get_orientation()
    W=hwW
    h=hwH    
    if deg==0:
        x=phyX
        y=H - 1 - phyY
        hwW=W
        hwH=H        
    elif deg== 90:
        y= phyX
        x= phyY
        hwW=H
        hwH=W        
    elif deg == 180:
        x = W - 1 - phyX
        y = phyY
        hwW=W
        hwH=H
    elif deg ==270:
        x = W - 1 - phyY
        y = H - 1 - phyX
        hwW=H
        hwH=W 
    return x,y,hwW,hwH

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
            h=0
        elif justif=="D":
            h=2
        elif justif=="C":
            h=1
    else:
        h=3
            
    if centre=="H":
        v=0
    elif centre=="C":
        v=1
    else:
        v=2
    
    render_glyph.draw_text(text,x,y,color,backcolor,h,v)
  
def draw_bmp(fichier,x, y, centre="H"):
    render_image.load_bmp(fichier)
    bpp,w,h=render_image.get_size()
    if centre == "H":
        decallage = 0
    elif centre == "C":
        decallage = h // 2
    else:
        decallage = h
    render_image.draw_bmp( x, y, decallage)
   
def get_bmp_size():
    return render_image.get_size()

def get_zone():
    #récupère la zone/surface ou sera écrit le texte. pemet de nettoyer avant ou de colorer, ou de dessiner autour
    #format x,y,largeur,hauteur
    return render_glyph.get_zone()

def DateTime_Pc():
    #affichage de la date heure et pourcentage batterie en haut
    set_font_size(25)
    #j'écrit l'heure
    draw_text("%s" %(dt.read_time()),5,0,0,15,"G","H")
    #j'ecrit la valeur de la batterie
    draw_text("[%s %%]>" %(dt.read_bat()),0,0,0,15,"D","H")

@micropython.native
def MenuLigne(bmp,texte,size,Numligne, ecart):
    pos=Numligne*ecart
    d,w,h=get_orientation()
    draw_bmp(bmp,15,pos,"C")
    _,BmpWIDTH,BmpHEIGHT= get_bmp_size()
    set_font_size(size)
    draw_line(0,pos+50,w,pos+50,5)
    draw_line(0,pos-50,w,pos-50,5)
    set_font_size(size)
    draw_text(texte,BmpWIDTH +12 ,pos,0,15,"L","C")

#@mesure_time("paramligne")
def ParamLigne(texte,info,size,Numligne,ecart):
    pos=Numligne*ecart
    set_font_size(size)
    draw_text(texte,10,pos,0,15,"G","B")
    draw_text(info,10,pos,0,15,"D","B")

#@mesure_time("simpleligne")
def SimpleLigne(texte,justif,size,Numligne,ecart):
    pos=Numligne*ecart
    set_font_size(size)
    draw_text(texte,10,pos,0,15,justif,"C")

def PageEntete(fichier_bmp,texte):
    #entete des pages, toujours les même donc on fait une def
    set_orientation(90) #a 90 pour les menu, seul reader peut pivoter
    d,w,h=get_orientation() # je récupère les bonne dimension
    render_draw.draw_rect(0,0,w,h,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
    #affichage de la datetime ,pc
    DateTime_Pc()
    MenuLigne(fichier_bmp,texte,40,1,100)

