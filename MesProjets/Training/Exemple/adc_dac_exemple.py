from pyb import Timer, Pin, ADC, DAC

from utime import sleep_ms

tim = Timer(1, freq=1000) # Définition du timer 1 à la fréquence 1000Hz

adc_pos = ADC(Pin('X11')) # Convertisseur analogique-numérique sur la pin 11

adc_neg = ADC(Pin('X12')) # Convertisseur analogique-numérique sur la pin 12

dac = DAC(Pin('X5'), bits=12)   # Convertisseur CNA 12 bit sur la pin X5

K_P = 2.0

def correction_avec_timer():
    
    global K_P
    
    # Conversion numérique de la tension de sortie du système
    entree_pos = adc_pos.read() # Lecture du CAN
    entree_neg = adc_neg.read() # Lecture du CAN
    
    erreur = entree_pos - entree_neg
    
    erreur_corrigee = K_P*erreur
    
    dac.write(int(erreur_corrigee)) # Ecriture sur le CNA
    print(erreur)
    print(erreur_corrigee)
    sleep_ms(1)
    
while True:
    correction_avec_timer()
    
