"""Touch keyboard."""
from micropython import const  # type: ignore
import time

class TouchKeyboard(object):
    """Touchscreen keyboard only teturn key"""
    KEYS = (
        (
            ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'), #10
            ('a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'), #9
            ('\t', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '\b', '\b'), #10
            ('\n', ' ', '\r') #3
        ),
        (
            ('Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'), #10
            ('A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'), #9
            ('\t', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '\b', '\b'), #10
            ('\n', ' ', '\r') #3
        ),
        (
            ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'),
            ('@', '#', '$', '%', '^', '&', '*', '(', ')'),
            ('\f', '+', ',', '.', '-', '_', '!', '?', '\b', '\b'),
            ('\a', ' ', '\r')
        ),
        (
            ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'),
            ('<', '>', '|', '\\', '/', '{', '}', '[', ']'),
            ('\f', '=', '"', '\'', ';', ':', '`', '~', '\b', '\b'),
            ('\a', ' ', '\r')
        )
    )

    def __init__(self,xMin=0,yMin=0,xMax=960,yMax=520):
        """Initialize Keyboard.
        Args:
            x et y retour de position du touch. 
            xmin et ymin zone minimum du clavier
            xmax et ymax zone maximun du clavier (taille max de l ecran))
        """
        self.xmin=xMin
        self.ymin=yMin
        self.xmax=xMax
        self.ymax=yMax
        self.zonex=self.xmax-self.xmin
        self.zoney=self.ymax-self.ymin
        self.maxligne=len(self.KEYS[0])
        self.hauteurtouche=self.zoney/self.maxligne
        self.maxcolonnel0=len(self.KEYS[0][0])
        self.largeurtouche=self.zonex/self.maxcolonnel0
        self.maxcolonnel1=len(self.KEYS[0][1])
        self.kb_screen = 0
        self.kb_text = ''
        self.locked = False

    def clear_text(self):
        """Clear the keyboard text"""
        self.kb_text = ''

    def handle_keypress(self, xy):
        """Get  pressed key.
        Args:
            x, y (int): Pressed screen coordinates.
        Returns:
            bool: True indicates return pressed otherwise False
        """
        #x, y = y, x  # Touch coordinates need to be swapped.
        #la partie Y est la petite et X dans l'autre sens
        x,y=xy
        
        ligne= self.maxligne - 1-(y//self.hauteurtouche)
        print(ligne)
        if ligne < 0 :
            ligne =0
        if ligne > self.maxligne :
            ligne=self.maxligne
        
        if ligne == 0 or ligne == 2:
            colonne = x // (self.zonex/ self.maxcolonnel0)
        elif ligne == 1:
            colonne = x // (self.zonex/ self.maxcolonnel1)
        else:
            # Row 3 Zone del'espace central
            if x < self.largeurtouche:
                colonne = 0
            elif x > (self.xmax - self.largeurtouche):
                colonne = 2
            else:
                colonne = 1 # je suis sur l'espace
        print(colonne)
        
        thekey = self.KEYS[self.kb_screen][int(ligne)][int(colonne)]
        
        if thekey == '\t' or thekey == '\f':
            self.kb_screen ^= 1  # Toggle caps or flip symbol sets
            return "caps"
        elif thekey == '\a':
            self.kb_screen = 0  # Switch to alphabet screen
            return "alpha"
        elif thekey == '\n':
            self.kb_screen = 2  # Switch to numeric / symbols screen
            return "num"
        elif thekey == '\b':  # Backspace
            self.kb_text = self.kb_text[:-1]
            return "backspace"

        elif thekey == '\r':
            # Keyboard return pressed (start search)
            texte = self.kb_text
            self.kb_text =''
            return texte

        else:
            self.kb_text += thekey
            return thekey


if __name__ == "__main__":
    key = TouchKeyboard()
    print(key.handle_keypress((51,414)))

         