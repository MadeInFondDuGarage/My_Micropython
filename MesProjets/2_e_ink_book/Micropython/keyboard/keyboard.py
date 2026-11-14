import t547
from time import sleep
import random

import oxygen_mono as font

KEY_BACKSPACE = 0x08
KEY_SHIFT = '\x10'
KEY_SPACE = '\x20'
KEY_ENTER = '\x0D'

KEYBOARD = (
    (
        "~1234567890-+",
        "QWERTYUIOP[]",
        "ASDFGHJKL;'",
        "ZXCVBNM,./",
        f"{KEY_SHIFT}{KEY_SPACE}{KEY_ENTER}"
    ),
    (
        "`!@#$%^&*()_+",
        "qwertyuiop{}",
        "asdfghjkl:\"",
        "zxcvbnm<>?",
        "éàèëê€1234",
        f"{KEY_SHIFT}{KEY_SPACE}{KEY_ENTER}"
    )
)

class Keyboard():

    def __init__(self, display, font, keyboard=KEYBOARD):
        self.display = display
        self.shift = 0
        self.keyboard = keyboard
        self.font = font
        print(self.keyboard)

    def draw(self, x, y):
        """Draws the keyboard at the given position."""
        row = x
        col = y
        for i in range(len(self.keyboard[self.shift])):
            for j in range(len(self.keyboard[self.shift][i])):

                key = self.keyboard[self.shift][i][j]
                if key == KEY_SHIFT:
                    self.display.write(self.font, "[shift]", x + j * self.font.MAX_WIDTH, y + i * self.font.HEIGHT)
                elif key == KEY_SPACE:
                    self.display.write(self.font, "[space]", x + j * self.font.MAX_WIDTH, y + i * self.font.HEIGHT)
                elif key == KEY_ENTER:
                    self.display.write(self.font, "[enter]", x + j * self.font.MAX_WIDTH, y + i * self.font.HEIGHT)
                else:
                    self.display.write(
                        self.font,
                        self.keyboard[self.shift][i][j],
                        x + j * self.font.MAX_WIDTH,
                        y + i * self.font.HEIGHT)

display = t547.T547()
display.init()
display.power(True)
display.clear()
#display.rotation(display.PORTRAIT)
width = display.width()
height = display.height()

kbd = Keyboard(display, font)
kbd.shift=1
kbd.draw(0, 0)

display.show()
display.power(False)
