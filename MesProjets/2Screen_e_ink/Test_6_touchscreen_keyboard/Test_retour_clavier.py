def in_zone_line(pos, Numligne, ecart,espacement=75):
    tap,x,y=pos
    zone_y1=Numligne*ecart-espacement
    zone_y2=Numligne*ecart+espacement
    return zone_y1 <= y <= zone_y2

def val_clav_num(pos,string_val_clavier,nbr_max=2):
    #pos pour le retour touchscreen,
    tiers= 540//3
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
            string_val_clavier=str(int(string_val_clavier)//10)
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
        string_val_clavier+=str(touch)
        string_val_clavier=string_val_clavier[-nbr_max:]

    return touch,string_val_clavier


