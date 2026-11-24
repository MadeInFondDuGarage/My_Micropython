import micropython
import utime

import render_image_4bpp as render_image
import render_draw_4bpp as render_draw
import render_glyph_4bpp as render_glyph

def mesure_time(label=None):

    def decorator(func):
        name = label or func.__name__

        def wrapper(*args, **kwargs):
            start = utime.ticks_us()
            result = func(*args, **kwargs)
            end = utime.ticks_us()

            print("[TIME] {} -> {} ms".format(
                name,
                utime.ticks_diff(end, start)/1000
            ))

            return result

        return wrapper

    return decorator

@micropython.viper
def scale_coord(v: int, scale_q8: int) -> int:
    return (v * scale_q8) >> 8

class Render:
    """
    Moteur de rendu pour fonte Hershey, dessin et bitmap
    """
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
    
    def __init__(self,buf,width,height):
        self.FONT_UNITS_HEIGHT = 120   # hauteur logique normalisée (TARGET_RANGE)
        self.FONT_SPACE = 10           # espace par défaut si glyph absent
        self.ORIENTATION=0
        self.TEXT=""
        self.PARSED_TEXT=[]
        self.SCALE=1
        self.FONT_SIZE=30
        self.TITRE=1
        self.JUSTIF="G" #postion latéral en X
        self.CENTRE="B" #centrage du texte par défaut lier au bas. si je met 0 en y quelque soit la taille du texte on le vois parraitre

        self.X=0
        self.Y=0
        self.BACKCOLOR=0
        self.BUF=buf
        self.WIDTH=width
        self.HEIGHT=height
        self.HwWIDTH=width #hardware largeur
        self.HwHEIGHT=height #hardware hauteur
        
        render_draw.set_context(self.BUF, self.HwWIDTH, self.HwHEIGHT)
        render_glyph.set_context(self.BUF, self.HwWIDTH, self.HwHEIGHT)
        
        self._BmpFICHIER = "" #chemin du fichier
        self.BmpWIDTH  = None #largeur
        self.BmpHEIGHT = None #hauteur
        self._BmpBPP   = None
    
    def set_font(self,font_module):
        # on ouvre un FICHIER binaire
        render_glyph.set_font(font_module)
        
    # ---------- Chargement ----------
    @mesure_time("load_bmp")
    def set_bmp(self, fichier):
        self._BmpFICHIER = fichier
        self.BmpWIDTH, self.BmpHEIGHT, self._BmpBPP = render_image.bmp_load(fichier)
            
    # -----------Rotate ---------
    def set_orientation(self,deg):
        #definie l'orientation de l'écriture des polices sur l'écran
        if deg > -1 and deg < 90:
            deg=0
            self.WIDTH=self.HwWIDTH
            self.HEIGHT=self.HwHEIGHT
        elif deg > 89 and deg <180 :
            deg= 90
            self.WIDTH=self.HwHEIGHT
            self.HEIGHT=self.HwWIDTH
        elif deg > 179 and deg < 269:
            deg=180
            self.WIDTH=self.HwWIDTH
            self.HEIGHT=self.HwHEIGHT
        elif deg > 269 and deg < 360:
            deg = 270
            self.WIDTH=self.HwHEIGHT
            self.HEIGHT=self.HwWIDTH
        else:
            deg=0
            self.WIDTH=self.HwWIDTH
            self.HEIGHT=self.HwHEIGHT
        
        render_draw.set_orientation(deg)
        render_glyph.set_orientation(deg)
        self.ORIENTATION=deg
        
    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color):
        render_draw.draw_pixel(x, y, color)

    # ---------- Ligne ----------
    def draw_line(self, x1, y1, x2, y2, color):
        #dessine une ligne dans le buffer
        render_draw.draw_line(x1, y1, x2, y2, color)
            
    # ---------- Texte et bmp ---------- 
    def set_text(self,text):
        #definition du texte a afficher
        self.TEXT=text
        
    def set_font_size(self,font_size_px):
        #definition de la taille de la police
        self.FONT_SIZE=font_size_px
        render_glyph.set_font_size(font_size_px)
        
    def set_titre(self,titre):
        #définition de la taille des titre pour faire l'équivalent des h1 a h6
        render_glyph.set_titre(titre)
        
    
    @mesure_time("draw_text")
    def draw_text(self, x, y, color, backcolor=-1,justif="L",centre="H"):
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
        
        render_glyph.draw_text(self.TEXT,x,y,color,backcolor,h,v)
  
    
    def draw_bmp(self, x, y, centre="H"):
        self.set_orientation(self.ORIENTATION)
        if centre == "H":
            decallage = 0
        elif centre == "C":
            decallage = self.BmpHEIGHT // 2
        else:
            decallage = self.BmpHEIGHT
        render_image.bmp_draw(self.BUF, self.HwWIDTH, self.HwHEIGHT,
                              self.ORIENTATION, x, y, decallage)
                
   
    @mesure_time("get_zone")
    def get_zone(self):
        #récupère la zone/surface ou sera écrit le texte. pemet de nettoyer avant ou de colorer, ou de dessiner autour
        #format x,y,largeur,hauteur
        return render_glyph.get_zone()
        
        
                
            



