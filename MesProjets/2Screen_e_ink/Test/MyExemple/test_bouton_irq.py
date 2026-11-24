from machine import ADC,Pin,Timer, I2C,SPI


def test_bouton_irq():
    #---------------Les boutons
    #Bouton
    BUTTON_0 =0
    BUTTON_1 =21
    bouton_0 =Pin(BUTTON_0,Pin.IN) # bouton du boot 0
    bouton_1= Pin(BUTTON_1,Pin.IN) # bouton 2
    #interruption sur les boutons
    bouton_1.irq(trigger=Pin.IRQ_FALLING,handler=bouton)

def bouton(t):
    print("Bouton 0:", bouton_0.value())       # get value, 0 or 1
    print("Bouton 1:", bouton_1.value())       # get value, 0 or 1
    print("Valeur entrée batterie:", val_16,"/",val/500000)
    machine.idle()
    
if __name__ == "__main__":
    #interruption sur les boutons
    test_bouton_irq()