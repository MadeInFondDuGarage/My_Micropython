import machine
from machine import ADC,Pin,Timer, I2C,SPI


def bat_voltage():
    #Batterie
    BATT_PIN =14
    adc = ADC(BATT_PIN)        # create an ADC object acting on a pin
    #---------------mesure de la baterie
    val_16 = adc.read_u16()  # valeur lue sur 16bit (0-65535)
    val = adc.read_uv()/500000   # valeur lue en microvolts et ramener en volt
    print(val)
    
if __name__=="__main__":
    bat_voltage()