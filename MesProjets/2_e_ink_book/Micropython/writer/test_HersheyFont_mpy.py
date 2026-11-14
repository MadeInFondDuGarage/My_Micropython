import t547
import hershey_font

# ------------------------------------------------------------
# Initialisation écran
# ------------------------------------------------------------
screen = t547.T547()
screen.init()
screen.clear()

buf = screen.get_buffer()
width = screen.width()
height = screen.height()

# ------------------------------------------------------------
# Chargement de la fonte binaire
# ------------------------------------------------------------
with open("hershey_gothic.bin", "rb") as f:
    font_bin = f.read()

# ------------------------------------------------------------
# Exemples de rendu texte
# ------------------------------------------------------------

# Texte standard
hershey_font.draw_text_bin(
    font_bin,
    20,  60,                     # x, y (baseline)
    "Bonjour",
    255,                          # couleur
    buf,
    width, height,
    20                            # hauteur du texte en pixels
)

# Texte plus grand
hershey_font.draw_text_bin(
    font_bin,
    20, 120,
    "Texte vectoriel",
    255,
    buf,
    width, height,
    40
)

# Très grand texte
hershey_font.draw_text_bin(
    font_bin,
    20, 220,
    "XXL",
    255,
    buf,
    width, height,
    80
)

# ------------------------------------------------------------
# Affichage
# ------------------------------------------------------------
screen.show()