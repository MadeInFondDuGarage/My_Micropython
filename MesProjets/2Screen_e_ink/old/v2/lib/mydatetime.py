import myglobal
import myrenderdisplay as rd

from machine import ADC

def bat_voltage():
    #Batterie
    BATT_PIN =14
    adc = ADC(BATT_PIN)        # create an ADC object acting on a pin
    #---------------mesure de la baterie
    val = adc.read_uv()//5000   # valeur lue en microvolts et ramener en volt
    pc=(val-320)
    return pc


def DateTime_Pc():
    #affichage de la date heure et pourcentage batterie en haut
    rd.set_font_size(25)
    
    #j'écrit l'heure
    rd.draw_text("%s" %(myglobal.i2c_rtc.read_time()),5,0,0,15,"G","H")

    #j'ecrit la valeur de la batterie
    rd.draw_text("[%s %%]>" %(bat_voltage()),0,0,0,15,"D","H")
    