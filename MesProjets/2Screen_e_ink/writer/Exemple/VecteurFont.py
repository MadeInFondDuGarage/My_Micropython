import micropython

@micropython.viper
def scale_coord(v: int, scale_q8: int) -> int:
    return (v * scale_q8) >> 8

class VecteurFontPy:
    """
    Moteur de rendu pour fonte Hershey chargée depuis un module .py
    (debug, pédagogique, ou fonte freezée)
    """

    FONT_UNITS_HEIGHT = 120   # hauteur logique normalisée (TARGET_RANGE)
    FONT_SPACE = 10           # espace par défaut si glyph absent
    ORIENTATION=0
    TEXT=""
    SCALE=1
    FONT_SIZE=30
    TITRE=1
    JUSTIF="G"
    BUF=""
    HwWIDTH=0
    WIDTH=0
    HwHEIGHT=0
    HEIGHT=0
    X=0
    Y=0
    BACKCOLOR=0
    HELP="""Moteur de rendu pour fonte de type Hershey qui vs avec les extensions inkscape 
                init: buffer externe, largeur du buffer, hauteur du buffer (init du module et infos de l'écran) 
                set_font : font (memory view ou .py des fonts) 
                set_orientation : 0,90,180,270. (représente les orientations du rendu dans le buffer) 
                draw_pixel: x,y,couleur ( ecris un pixel dans le buffer, couleur de 0 a 255, 0 = blanc 255 = noir)
                draw_line: x1,y1,x2,y2,couleur (ecris une ligne dans le buffer couleur comme le pixel)
                set_text: chaine du texte a écrire
                set_font_size: taille du rendu de la font en pixel de haut 
                set_titre: de 0 a 6, pour adapter la taille de la font proportionnelement au choix initial de la taille de la font
                set_justif:"L","G","C","D" justification libre, gauche, centre et droite sur lécran. avec D,C,G le x n'est pas pris en compte. on est toujours avec un x=5
                draw_text:x,y,couleur font, couleur de fond (dessine le texte a la position demder, avec la couleur 0 a 255. la couleur de fond est de -1 (aucune nettoyage du buffer), 0 a 255)
                get_zone: renvoie x,y,largeur,hauteur de la zone qui est occuper par le texte. permet de nettoyer l'écran avant sur des eink
                """
    
    def __init__(self,buf,width,height):
        self.BUF=buf
        self.WIDTH=width
        self.HEIGHT=height
        self.HwWIDTH=width #hardware largeur
        self.HwHEIGHT=height #hardware hauteur
    
    def set_font(self,font_module):
        self.font = font_module
        
    # -----------Rotate ---------
    def set_orientation(self,deg):
        #definie l'orientation de l'écriture des polices sur l'écran
        if deg > -1 and deg < 90:
            deg=0
        elif deg > 89 and deg <180 :
            deg= 90
        elif deg > 179 and deg < 269:
            deg=180
        elif deg > 269 and deg < 360:
            deg = 270
        else:
            deg=0
        self.ORIENTATION=deg
        
    @micropython.native
    def _rotate(self,x,y):
        #je renvoir a travers le filtre au cas ou on est injecter une valeur directement dans le slef.ORIENTATION
        self.set_orientation(self.ORIENTATION)
        phyX=x
        phyY=y
        self.WIDTH=self.HwWIDTH
        self.HEIGHT=self.HwHEIGHT
        
        if self.ORIENTATION==0:
            self.WIDTH=self.HwWIDTH
            self.HEIGHT=self.HwHEIGHT
            phyX=x
            phyY=y
            
        elif self.ORIENTATION== 90:
            self.WIDTH=self.HwHEIGHT
            self.HEIGHT=self.HwWIDTH
            phyX = y
            phyY = self.HwHEIGHT - 1 - x
            
        elif self.ORIENTATION == 180:
            self.WIDTH=self.HwWIDTH
            self.HEIGHT=self.HwHEIGHT
            phyX = self.HwWIDTH - 1 - x
            phyY = self.HwHEIGHT - 1 - y
            
        elif self.ORIENTATION ==270:
            self.WIDTH=self.HwHEIGHT
            self.HEIGHT=self.HwWIDTH
            phyX = self.HwWIDTH - 1 - y
            phyY = x
        return phyX,phyY
        
    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color):
        #dessine 
        color = 255 - color
        
        if x < 0 or x >= self.HwWIDTH or y < 0 or y >= self.HwHEIGHT:
            return

        pos = (y * self.HwWIDTH // 2) + (x // 2)
        pixel = self.BUF[pos]

        if x & 1:
            pixel = (pixel & 0x0F) | (color & 0xF0)
        else:
            pixel = (pixel & 0xF0) | (color >> 4)

        self.BUF[pos] = pixel

    # ---------- Ligne ----------
    @micropython.native
    def draw_line(self, xx1, yy1, xx2, yy2, color):
        #dessine une ligne dans le buffer
        x1,y1=self._rotate(xx1,yy1)
        x2,y2=self._rotate(xx2,yy2)
        
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.draw_pixel(x1, y1, color)

            if x1 == x2 and y1 == y2:
                break

            e2 = err << 1
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    # ---------- Mise à l’échelle ----------
    @micropython.native
    def _compute_scale(self, font_size_px):
        # Q8.8 fixe – identique .py / .bin
        return (font_size_px << 8) // self.FONT_UNITS_HEIGHT
    
    # ---------- Texte ----------
    @micropython.native
    def set_text(self,text):
        #definition du texte a afficher
        self.TEXT=text
        
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
            
    @micropython.native
    def draw_text(self, x, y, color, backcolor=-1,justif="L"):
        # je met le backcolor a -1 par défaut car pas forcement nécéssaire et -1 enlever le remplissage du buffer
        self.SCALE = self._compute_scale(int(self.FONT_SIZE*self.TITRE))
        if justif!="L":
            zone=self.get_zone() #je récupère les dimensions du texte
            if justif=="G":
                x=5
            elif justif=="D":
                x=self.WIDTH-zone[2]
            else:
                x=self.WIDTH//2-zone[2]//2
                
        self.X=x
        self.Y=y
        
        
        if backcolor > -1:
            self.BACKCOLOR = backcolor
            self._clean()
            
        scale=self.SCALE
        
        cx = x
        
        for ch, style in self._parse_styled(self.TEXT):
            code = ord(ch)
            if code not in self.font.GLYPH_INDEX:
                cx += self.FONT_SIZE // 3
                continue

            # Différent du .bin :
            # on lit directement les structures Python
            glyph_id, advance, _ = self.font.GLYPH_INDEX[code]
            _, segments = self.font.GLYPH_DATA[glyph_id]
            
            for x1, y1, x2, y2 in segments:
                if style==0:
                    style_ligne_1=0
                    style_ligne_2=0
                    gras_max=1
                    
                if style==1:
                    style_ligne_1=0
                    style_ligne_2=0
                    gras_max=3
                    
                if style==2:
                    style_ligne_1=(scale_coord(y1, scale)//3)
                    style_ligne_2=(scale_coord(y2, scale)//3)
                    gras_max=1
                
                if style==3:
                    style_ligne_1=(scale_coord(y1, scale)//3)
                    style_ligne_2=(scale_coord(y2, scale)//3)
                    gras_max=3
                    
                for gras in range(0,gras_max):    
                    self.draw_line(
                        cx + gras + style_ligne_1 + scale_coord(x1, scale) ,
                        y  - scale_coord(y1, scale) ,
                        cx + gras + style_ligne_2 + scale_coord(x2 , scale) ,
                        y  - scale_coord(y2, scale) ,
                        color
                    )
                    
            cx += scale_coord(advance, scale)
            
    @micropython.native
    def get_text(self):
        #renvoie le texte ajuster par rapport a la taille de l'écran/taille des font et place dispo
        size_total=0
        size=0            
        for ch in range(0,len(self.TEXT)):
            code = ord(self.TEXT[ch])
            if code not in self.font.GLYPH_INDEX:
                continue
            glyph, advance, _ = self.font.GLYPH_INDEX[code]
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
        
        for ch, style in self._parse_styled(self.TEXT):
            code = ord(ch)
            if code not in self.font.GLYPH_INDEX:
                cx += self.FONT_SIZE // 3
                continue

            # Différent du .bin :
            # on lit directement les structures Python
            glyph_id, advance, _ = self.font.GLYPH_INDEX[code]
            _, segments = self.font.GLYPH_DATA[glyph_id]
            
            for x1, y1, x2, y2 in segments:
                Y1=scale_coord(y1, scale)
                Y2=scale_coord(y2, scale)
                if Y1 > max_y or Y2 > max_y:
                   max_y=max(Y1,Y2)
                if Y1 < min_y or Y2 < min_y:
                    min_y=min(Y1,Y2)
            cx += scale_coord(advance, scale)
        
        return self.X,self.Y-2-max_y,(cx+scale_coord(advance, scale))-self.X,max(max_y,min_y)-min(max_y,min_y)+4
            
        
        
                
            


