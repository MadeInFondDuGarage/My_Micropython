
from pyb import Timer, Pin, ADC, DAC

tim = Timer(1, freq=1000) # Définition du timer 1 à la fréquence 1000Hz

adc_pos = ADC(Pin('X11')) # Convertisseur analogique-numérique sur la pin 11

adc_neg = ADC(Pin('X12')) # Convertisseur analogique-numérique sur la pin 12

dac = DAC(Pin('X5'), bits=12)   # Convertisseur CNA 12 bit sur la pin X5

#K_P = 2.0

def correction_avec_timer(_):
    K_P=2.0
    try:
        erreurCorrigee =K_P*3
    except:
        print('erreur')
    else:
        print(erreurCorrigee)
    

# Fonction qui se déclenche à chaque fois que le timer finit sa boucle
tim.callback(correction_avec_timer)  