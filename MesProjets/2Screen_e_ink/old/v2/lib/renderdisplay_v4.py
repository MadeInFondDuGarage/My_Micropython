import micropython
import utime
import render_image_4bpp as render_image
import render_draw_4bpp as render_draw

import gc

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
            print("mem:",gc.mem_free())

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
        
        self._BmpFICHIER = "" #chemin du fichier
        self.BmpWIDTH  = None #largeur
        self.BmpHEIGHT = None #hauteur
        self._BmpBPP   = None
    
    def set_font(self,font_module):
        # on ouvre un FICHIER binaire
        self.f = open(font_module, "rb")
        self._read_header()
        self._read_index()
        
    # ---------- Chargement ----------
    @mesure_time("load_bmp")
    def set_bmp(self, fichier):
        self._BmpFICHIER = fichier
        self.BmpWIDTH, self.BmpHEIGHT, self._BmpBPP = render_image.bmp_load(fichier)
    
    @micropython.native
    def _read_header(self): #lecture de l'entete
        data = self.f.read(6)
        self.glyph_count = data[0] | (data[1] << 8)
        self.ascent = data[2] | (data[3] << 8)
        self.descent = data[4] | (data[5] << 8)
        
    @micropython.native
    def _read_index(self): #lecture des indexs
        # unicode → offset
        self.index = {}
        for _ in range(self.glyph_count):
            raw = self.f.read(6)
            code = raw[0] | (raw[1] << 8)
            offset = raw[2] | (raw[3] << 8) | (raw[4] << 16) | (raw[5] << 24)
            self.index[code] = offset
            
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
        self.ORIENTATION=deg
        
        
    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color):
        render_draw.draw_pixel(x, y, color)

    # ---------- Ligne ----------
    @micropython.native
    def draw_line(self, x1, y1, x2, y2, color):
        #dessine une ligne dans le buffer
        render_draw.draw_line(x1, y1, x2, y2, color)
        
    # ---------- Mise à l’échelle ----------
    @micropython.native
    def _compute_scale(self, font_size_px):
        # Q8.8 fixe – identique .py / .bin
        return (font_size_px << 8) // self.FONT_UNITS_HEIGHT

    @micropython.native
    def _read_int8(self):
        #lecture des valeur int 8 bits du fichier
        v = self.f.read(1)[0] # a chaque appel de cette fonction j'avance de 1 (1) dans le fichier et je lit 1bit [0]
        return v - 256 if v > 127 else v
    
    # ---------- Texte et bmp ---------- 
    @micropython.native
    def set_text(self,text):
        #definition du texte a afficher
        self.TEXT=text
        self.PARSED_TEXT=list(self._parse_styled(text))
        
    @micropython.native
    def set_font_size(self,font_size_px):
        #definition de la taille de la police
        self.FONT_SIZE=font_size_px
        
    @micropython.native
    def set_titre(self,titre):
        #définition de la taille des titre pour faire l'équivalent des h1 a h6
        ratio=[1,
               2, #taille 1
               1.9, #2
               1.7, #3
               1.5, #4
               1.3, #5
               1.2, #6
               1]
        if titre < 0 or titre > 6:
            titre=0
        self.TITRE=ratio[titre]
        
    @micropython.native    
    def _parse_styled(self,text):
        #nano parser pour trouver le style dans une phrase
        # avec des yield donc on exécute a chaque appel du for
        STYLE_NORMAL = 0
        STYLE_BOLD   = 1
        STYLE_ITALIC = 2
        style = STYLE_NORMAL
        i = 0
        while i < len(text):
            if text[i] == '<': #je cherche l'ouverture
                end = text.find('>', i) #jeregarde si j'ai la fermeture
                if end == -1: #sinon
                    yield (text[i], style) #je balance la sortie
                    i += 1
                    continue
                tag = text[i+1:end].strip().lower() #je découpe pour récupérer juste le tag
                i = end + 1 #j'avance apres tag
                if   tag in ('b', 'strong'):  style |= STYLE_BOLD # ici j'attribue le tag
                elif tag in ('i', 'em'):      style |= STYLE_ITALIC
                elif tag in ('/b', '/strong'): style &= ~STYLE_BOLD
                elif tag in ('/i', '/em'):     style &= ~STYLE_ITALIC
                # autres tags ignorés
            else:
                yield (text[i], style) #je renvoie le tous
                i += 1 #et j'avance
    
    @mesure_time("draw_text")
    @micropython.native
    def draw_text(self, x, y, color, backcolor=-1,justif="L",centre="H"):
        # je met le backcolor a -1 par défaut car pas forcement nécéssaire et -1 enlever le remplissage du buffer
        
        #je repasse la valeur de l'orientation dans le filtre au cas ou on ait passer en direct
        self.set_orientation(self.ORIENTATION)
        
        self.SCALE = self._compute_scale(int(self.FONT_SIZE*self.TITRE))
        zone=self.get_zone() #je récupère les dimensions du texte
        if justif!="L":
            if justif=="G":
                x=5
            elif justif=="D":
                x=self.WIDTH-zone[2]
            else:
                x=self.WIDTH//2-zone[2]//2
                
        if centre=="H":
            y=y+zone[3]+2
        elif centre=="C":
            y=y+zone[3]//2
            
        self.X=x
        self.Y=y
        
        
        if backcolor > -1:
            self.BACKCOLOR = backcolor
            self._clean()
            
        scale=self.SCALE
        
        cx = x
        
        for ch, style in self.PARSED_TEXT:
            code = ord(ch)
            if code not in self.index:
                cx += self.FONT_SIZE // 3
                continue
            
            # on va lire la fonte à la volée
            #je me position devant le caractère a lire
            self.f.seek(self.index[code])
            hdr = self.f.read(2)
            advance = hdr[0]
            seg_count = hdr[1]
            raw = self.f.read(seg_count * 4)
                      
            for s in range(seg_count):
                #je récupère les segments de la fonts directement. la taille est segment
                b = s * 4
                v = raw[b];     x1 = v - 256 if v > 127 else v
                v = raw[b+1];   y1 = v - 256 if v > 127 else v
                v = raw[b+2];   x2 = v - 256 if v > 127 else v
                v = raw[b+3];   y2 = v - 256 if v > 127 else v
                
                if style==0:
                    style_ligne_1=0
                    style_ligne_2=0
                    gras_max=2
                    
                if style==1:
                    style_ligne_1=0
                    style_ligne_2=0
                    gras_max=4
                    
                if style==2:
                    style_ligne_1=(scale_coord(y1, scale)//3)
                    style_ligne_2=(scale_coord(y2, scale)//3)
                    gras_max=2
                
                if style==3:
                    style_ligne_1=(scale_coord(y1, scale)//3)
                    style_ligne_2=(scale_coord(y2, scale)//3)
                    gras_max=3
                    
                for gras in range(0,gras_max):    
                    self.draw_line(
                        cx + gras + style_ligne_1 + scale_coord(x1, scale) ,
                        y   + gras -scale_coord(y1, scale) ,
                        cx + gras + style_ligne_2 + scale_coord(x2 , scale) ,
                        y   + gras -scale_coord(y2, scale) ,
                        color
                    )
                    
            cx += scale_coord(advance, scale)
    
    @micropython.native
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
                
    @micropython.native
    def get_text(self):
        #renvoie le texte ajuster par rapport a la taille de l'écran/taille des font et place dispo
        size_total=0
        size=0            
        for ch in range(0,len(self.TEXT)):
            code = ord(self.TEXT[ch])
            if code not in self.index:
                continue
            #je me position devant le caractère a lire
            self.f.seek(self.index[code])
            advance = self.f.read(1)[0] #je récupère sont pas
            size=scale_coord(advance, self.SCALE)
            if (size_total+size)> self.WIDTH:
                return self.TEXT[:ch],self.TEXT[ch:]
            else:
                size_total=size_total+size
        
        return self.TEXT
    
    @micropython.native
    def _clean(self):
        #clean de la zone ou sera écrit le texte
        zone=self.get_zone()
        for  h in range(0,zone[3]):
            self.draw_line(zone[0],zone[1]+h,zone[0]+zone[2],zone[1]+h,self.BACKCOLOR)
    
    @mesure_time("get_zone")
    @micropython.native
    def get_zone(self):
        #récupère la zone/surface ou sera écrit le texte. pemet de nettoyer avant ou de colorer, ou de dessiner autour
        #format x,y,largeur,hauteur
        scale=self.SCALE
        min_y=0
        max_y=0
        height=0
        width=0
        cx = self.X
        
        for ch, style in self.PARSED_TEXT:
            code = ord(ch)
            if code not in self.index:
                cx += self.FONT_SIZE // 3
                continue

             #je me position devant le caractère a lire
            self.f.seek(self.index[code])
            hdr = self.f.read(2)
            advance = hdr[0]
            seg_count = hdr[1]
            raw = self.f.read(seg_count * 4)
                      
            for s in range(seg_count):
                #je récupère les segments de la fonts directement. la taille est segment
                b = s * 4
                v = raw[b+1];   y1 = v - 256 if v > 127 else v
                v = raw[b+3];   y2 = v - 256 if v > 127 else v
                
                Y1=scale_coord(y1, scale)
                Y2=scale_coord(y2, scale)
                if Y1 > max_y or Y2 > max_y:
                   max_y=max(Y1,Y2)
                if Y1 < min_y or Y2 < min_y:
                    min_y=min(Y1,Y2)
            cx += scale_coord(advance, scale)
        
        return self.X,self.Y-2-max_y,(cx+scale_coord(advance, scale))-self.X,max(max_y,min_y)-min(max_y,min_y)+4
            
        
        
                
            



