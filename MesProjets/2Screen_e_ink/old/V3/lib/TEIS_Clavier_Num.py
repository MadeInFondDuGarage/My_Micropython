import TEIS_Render as Render

"""Module pour afficher un clavier numérique en bas de l'écran, non soumis a l'orientation car utilisable uniquement verticalement
l'utilisation du module est plus adapter car aucune instance multiple n'est prévue ni souhaitable"""

#variable pour le clavier. elle est global car persistante et nécéssaire pou une init externe
string_clavier=""

@micropython.native
def in_zone_line(pos, Numligne, ecart,espacement=75):
    #renvoie un bool en fonction si on est dans la zone de la ligne.
    #on peut soit mettre un multiple entre numligne et ecart (écart identique on on indique la ligne pretique pour les préférence ou ligne multiple)
    #ou alors mettre la position en pixel dans numligne et mettre l'écart a 1.
    tap,x,y=pos
    zone_y1=Numligne*ecart-espacement
    zone_y2=Numligne*ecart+espacement
    return zone_y1 <= y <= zone_y2

@micropython.native
def show_clav_num(couleur=0):
    #dessine le clavier
    Render.set_font_size(70)
    Render.draw_text("1    2    3",0,600,couleur,15,"C","C")
    Render.draw_text("4    5    6",0,700,couleur,15,"C","C")
    Render.draw_text("7    8    9",0,800,couleur,15,"C","C")
    Render.draw_text("0   RT  OK",0,900,couleur,15,"C","C")
    
@micropython.native
def val_clav_num(pos,nbr_max=2):
    #pos pour le retour touchscreen,
    global string_clavier
    if string_clavier==None:
        string_clavier=""
    d,w,h=Render.get_orientation()
    tiers= w//3
    touch=-3
    if pos[1]<tiers:
        if in_zone_line(pos,6,100,50):
            touch=1
        if in_zone_line(pos,7,100,50):
            touch=4
        if in_zone_line(pos,8,100,50):
            touch=7
        if in_zone_line(pos,9,100,50):
            touch=0
    elif tiers < pos[1] < tiers*2:
        if in_zone_line(pos,6,100,50):
            touch=2
        if in_zone_line(pos,7,100,50):
            touch=5
        if in_zone_line(pos,8,100,50):
            touch=8
        if in_zone_line(pos,9,100,50):
            touch=-1 #retour
            string_clavier=str(int(string_clavier)//10)
    elif tiers*2 < pos[1] < tiers*3:
        if in_zone_line(pos,6,100,50):
            touch=3
        if in_zone_line(pos,7,100,50):
            touch=6
        if in_zone_line(pos,8,100,50):
            touch=9
        if in_zone_line(pos,9,100,50):
            touch=-2 #ok
    if touch>= 0:
        string_clavier+=str(touch)
        string_clavier=string_clavier[-nbr_max:]

    return touch,string_clavier


