"""
 librairie simple pour la lecture de bmp
 pour la veserion en 24 on utilise
 Niveaux de gris : (R + G + B) // 3 ou pondéré (R*299 + G*587 + B*114) // 1000 (perception humaine)
"""
import micropython

class read_bmp():

    def __init__( self, path, check=True ):
            """ open a BMP file. The stream must be a FileIO opended on target file """
            self.path 	 = path #chemin du fichier
            self.offset  = None #debut de la trame bitmap
            self.width    = None #largeur
            self.height   = None #hauteur
            self.bpp      = None    # nombre de pixel par bits
            self.compression = None # Compression algorithm
            self.couleurs = None # Nbre de couleur
            self._load_bmp()
    
    
    def _load_bmp(self):
        with open(self.path, 'rb') as f:
            data = f.read()
        
        # Vérif signature BMP
        if data[0:2] != b'BM':
            raise ValueError("Not a BMP file")
        
        # Vérif nb couleurs (offset 46 = biClrUsed, 0 = toutes)
        self.bpp = int.from_bytes(data[28:30], 'little')
        if self.bpp not in (1, 2, 4, 8, 24):
            raise ValueError(f"Too many colors: {bpp}bpp (max 4bpp = 16 colors)")
        #vérification si il est compresser
        self.compression=int.from_bytes(data[30:34], 'little')
        if self.compression != 0:
            raise ValueError(f"Compressed BMP not supported ({compression})")
        
        # Dimensions
        self.width  = int.from_bytes(data[18:22], 'little')
        self.height = int.from_bytes(data[22:26], 'little')
        
        # Offset pixel data
        self.offset = int.from_bytes(data[10:14], 'little')
        
        # Copie dans bytearray
        self.buf = bytearray(data[self.offset:])
    
    
    def pixels(self):
        My_pixels = []
        row_bytes = (self.width * self.bpp + 31) // 32 * 4 # ajustement pour etre compatible avec le bmp

        if self.bpp == 1: # pour les noir et blanc
            for y in range(self.height): #sur la hauteur
                row = []
                base = y * row_bytes # on ce place sur le début de la ligne
                for x in range(self.width): # pour la partie x
                    row.append((self.buf[base + x // 8] >> (7 - x % 8)) & 1) # pour chaqu pixel je décalle
                My_pixels.append(row)

        elif self.bpp == 4:# pour les 16nivaeux d gris
            for y in range(self.height): #sur la hauteur
                row = []
                base = y * row_bytes # on ce place sur le début de la ligne
                for x in range(self.width): # pour la partie x
                    b = self.buf[base + x // 2] # ici je récupère l'octet
                    row.append(b >> 4 if x % 2 == 0 else b & 0x0F) # et suivant si il est pair ou pas je lis que le quartet utile.
                My_pixels.append(row)

        elif self.bpp == 8:#pour les 256 couleurs
            for y in range(self.height): #sur la hauteur
                base = y * row_bytes # on ce place sur le début de la ligne
                My_pixels.append(list(self.buf[base:base + self.width])) #la pas de soucis puisque on utilise l'octet entier
        
        elif self.bpp == 24:#pour les 24bits rgb qui sont inverse dans les bitmap couleurs
            row_bytes = (self.width * 3 + 3) & ~3
            for y in range(self.height): #sur la hauteur
                row = []
                base = y * row_bytes # on ce place sur le début de la ligne
                for x in range(self.width):
                    p = base + x * 3
                    row.append((self.buf[p+2] * 299 + self.buf[p+1] * 587 + self.buf[p] * 114) // 1000)
                My_pixels.append(row)

        return My_pixels

    
    def to4bpp(self):
        row_bytes = (self.width * self.bpp + 31) // 32 * 4
        result = bytearray(self.height * ((self.width + 1) // 2))
        idx = 0

        if self.bpp == 1:
            for y in range(self.height):
                base = y * row_bytes
                for x in range(0, self.width, 2):
                    hi = ((buf[base + x // 8] >> (7 - x % 8)) & 1) * 15
                    lo = ((buf[base + (x+1) // 8] >> (7 - (x+1) % 8)) & 1) * 15 if x + 1 < width else 0
                    result[idx] = (hi << 4) | lo
                    idx += 1

        elif self.bpp == 4:
            for y in range(self.height):
                base = y * row_bytes
                for x in range(0, self.width, 2):
                    result[idx] = buf[base + x // 2]
                    idx += 1

        elif self.bpp == 8:
            for y in range(self.height):
                base = y * row_bytes
                for x in range(0, self.width, 2):
                    hi = buf[base + x] >> 4
                    lo = buf[base + x + 1] >> 4 if x + 1 < self.width else 0
                    result[idx] = (hi << 4) | lo
                    idx += 1
                    
        elif self.bpp == 24:
                row_bytes = (self.width * 3 + 3) & ~3
                idx = 0
                for y in range(self.height):
                    base = y * row_bytes
                    for x in range(0, self.width, 2):
                        p = base + x * 3
                        pixel=(self.buf[p+2] * 299 + self.buf[p+1] * 587 + self.buf[p] * 114) // 1000
                        hi = pixel >> 4
                        lo = pixel >> 4 if x + 1 < self.width else 0
                        result[idx] = (hi << 4) | lo
                        idx += 1
        return result
    

