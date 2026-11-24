import t547
import render_image_4bpp as render_image
import render_draw_4bpp as render_draw
import render_glyph_4bpp as render_glyph

screen = t547.T547()
screen.init()

BUF,HwWIDTH,HwHEIGHT = screen.get_buffer(), screen.width(), screen.height()

#j'init le render d'écran
render_draw.set_context(BUF, HwWIDTH, HwHEIGHT)
render_image.set_context(BUF, HwWIDTH, HwHEIGHT)
render_draw.set_orientation(270)
render_image.set_orientation(270)
deg,W,H=render_draw.get_orientation()

render_draw.draw_rect(0,0,W,H,15,1) #j'efface le buffer grace a un rectangle plein en blanc.
screen.clear()

centre=250
hauteur=350
ecart=50

i=centre-78//2
j=hauteur
render_draw.draw_rect(0+i,0+j,78,120,0,1)
render_draw.draw_rect(4+i,4+j,70,100,15,1)
render_draw.draw_circle(13+i,13+j,5,0,1)
render_draw.draw_line(13+i,13+j,65+i,13+j,0)
render_draw.draw_line(13+i,23+j,65+i,23+j,0)
render_draw.draw_line(13+i,33+j,65+i,33+j,0)
render_draw.draw_line(13+i,43+j,65+i,43+j,0)
render_draw.draw_line(13+i,53+j,40+i,53+j,0)

i=centre-120//2
j=hauteur+120+ecart
render_draw.draw_rect(0+i,0+j,120,78,0,1)
render_draw.draw_rect(4+i,4+j,100,70,15,1)
render_draw.draw_circle(13+i,13+j,5,0,1)
render_draw.draw_line(13+i,13+j,80+i,13+j,0)
render_draw.draw_line(13+i,23+j,80+i,23+j,0)
render_draw.draw_line(13+i,33+j,80+i,33+j,0)
render_draw.draw_line(13+i,43+j,80+i,43+j,0)
render_draw.draw_line(13+i,53+j,60+i,53+j,0)

i=centre-78//2
j=hauteur+120+78+2*ecart
render_draw.draw_rect(0+i,0+j,78,120,0,1)
render_draw.draw_rect(4+i,16+j,70,100,15,1)
render_draw.draw_circle(13+i,23+j,5,0,1)
render_draw.draw_line(13+i,26+j,65+i,26+j,0)
render_draw.draw_line(13+i,36+j,65+i,36+j,0)
render_draw.draw_line(13+i,46+j,65+i,46+j,0)
render_draw.draw_line(13+i,56+j,65+i,56+j,0)
render_draw.draw_line(13+i,66+j,40+i,66+j,0)

i=centre - 120//2
j=hauteur+2*120+78+3*ecart
render_draw.draw_rect(0+i,0+j,120,78,0,1)
render_draw.draw_rect(16+i,4+j,100,70,15,1)
render_draw.draw_circle(33+i,13+j,5,0,1)
render_draw.draw_line(33+i,13+j,95+i,13+j,0)
render_draw.draw_line(33+i,23+j,95+i,23+j,0)
render_draw.draw_line(33+i,33+j,95+i,33+j,0)
render_draw.draw_line(33+i,43+j,95+i,43+j,0)
render_draw.draw_line(33+i,53+j,80+i,53+j,0)

render_image.load_bmp("themes/steampunk/Connexion WIFI.bmp")
render_image.draw_bmp(100,100,0)

screen.show()