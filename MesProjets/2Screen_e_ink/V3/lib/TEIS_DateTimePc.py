from machine import ADC,I2C,Pin

"""
    Module pour récupération et écriture dans le RTC de la board lilygo547.
    Ceci n'est pas une class, car utiliser 1 seul fois, ce qui limitte l'empreinte mémoire dans micropython de quelque Ko.
    les infos global sont présent pour la persistance de l'ensemble
"""
#global pour l'instance systeme i2c
I2C_RTC = None
#infos adresse i2c et zone mêmoire pour le rtc
ADDR=81
ADDR_MEM=0x02

# elements prédéfinie pour la board lilygo epd47 avec le controleur RTC PCF8563
def init_rtc(BOARD_SCL=17,BOARD_SDA=18,FREQ=400000):
    global I2C_RTC
    #init i2c hardware
    I2C_RTC = I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=FREQ)

def scan():
    return I2C_RTC.scan()

def _bcd2dec(bcd):
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def _dec2bcd(dec):
    return ((dec // 10 ) << 4 ) + dec % 10 #le double / divise en renvoyant uniquement l'entier

def read_time():
    a,mm,j,h, m, s = get_time()
    a +=2000
    return f"{j:02}/{mm:02}/{a:04} {h:02}:{m:02}"

def get_time():
    #je récupère l'heure en mode tupple
    datetime=I2C_RTC.readfrom_mem(ADDR,ADDR_MEM, 7)
    seconds = _bcd2dec(datetime[0])
    minutes = _bcd2dec(datetime[1] & 0x7F)
    # 0x3F pour les 24hrs
    heures = _bcd2dec(datetime[2] & 0x3F)
    
    jours = _bcd2dec(datetime[3])
    mois = _bcd2dec(datetime[5])
    annee = _bcd2dec(datetime[6])
    
    return annee,mois,jours,heures, minutes, seconds

def set_time(annee,mois,jours,heures, minutes, seconds):
    # j'injecte le réglage de la date et l'heure
    datetime=bytearray(7)
    #affectation dans un array
    datetime[6]=_dec2bcd(annee)
    datetime[5]=_dec2bcd(mois)
    datetime[4]=0
    datetime[3]=_dec2bcd(jours)
    datetime[2]=_dec2bcd(heures)
    datetime[1]=_dec2bcd(minutes)
    datetime[0]=0
    I2C_RTC.writeto_mem(ADDR,ADDR_MEM ,datetime)


"""
    Cette partie est l'usage de la batterie
"""

# init pin Batterie
adc= None

def init_bat():
    global adc
    BATT_PIN =14
    adc = ADC(BATT_PIN)        # create an ADC object acting on a pin
    
def read_bat():
    #---------------mesure de la baterie
    val = adc.read_uv()//5000   # valeur lue en microvolts et ramener en volt
    pc=(val-320)
    return pc


if __name__ == "__main__":
    
    init_bat()
    print("batterie :",read_bat())
    
    init_rtc()
    print("scan: ",scan())
    print("Date heure: ",read_time())
