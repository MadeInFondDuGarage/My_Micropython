from machine import I2C,Pin

#Simple ensemble d'éléments pour la lecture du rtc

class RTC():
    # elements prédéfinie pour la board lilygo epd47 avec le controleur RTC PCF8563
    def __init__(self,BOARD_SCL=17,BOARD_SDA=18,FREQ=400000,ADDR=81,ADDR_MEM=0x02):
        
        #transfert des info
        self.BOARD_SCL=BOARD_SCL
        self.BOARD_SDA=BOARD_SDA
        self.FREQ=FREQ
        self.ADDR=ADDR
        self.ADDR_MEM=ADDR_MEM
        
        #init i2c hardware
        self.i2c_rtc = I2C(scl=Pin(self.BOARD_SCL), sda=Pin(self.BOARD_SDA), freq=FREQ)
    
    def Set_AddrRtc(self,ADDR,ADDR_MEM):
        self.ADDR=ADDR
        self.ADDR_MEM=ADDR_MEM
    
    def scan(self):
        return self.i2c_rtc.scan()
    
    def _bcd2dec(self,bcd):
        return (bcd >> 4) * 10 + (bcd & 0x0F)

    def _dec2bcd(self,dec):
        return ((dec // 10 ) << 4 ) + dec % 10 #le double / divise en renvoyant uniquement l'entier
    
    def read_time(self):
        a,mm,j,h, m, s = self.get_time()
        a +=2000
        return f"{j:02}/{mm:02}/{a:04} {h:02}:{m:02}"
    
    def get_time(self):
        #je récupère l'heure en mode tupple
        datetime=self.i2c_rtc.readfrom_mem(self.ADDR,self.ADDR_MEM, 7)
        seconds = self._bcd2dec(datetime[0])
        minutes = self._bcd2dec(datetime[1] & 0x7F)
        # 0x3F pour les 24hrs
        heures = self._bcd2dec(datetime[2] & 0x3F)
        
        jours = self._bcd2dec(datetime[3])
        mois = self._bcd2dec(datetime[5])
        annee = self._bcd2dec(datetime[6])
        
        return annee,mois,jours,heures, minutes, seconds
    
    def set_time(self,annee,mois,jours,heures, minutes, seconds):
        # j'injecte le réglage de la date et l'heure
        datetime=bytearray(7)
        #affectation dans un array
        datetime[6]=self._dec2bcd(annee)
        datetime[5]=self._dec2bcd(mois)
        datetime[4]=0
        datetime[3]=self._dec2bcd(jours)
        datetime[2]=self._dec2bcd(heures)
        datetime[1]=self._dec2bcd(minutes)
        datetime[0]=0
        
        self.i2c_rtc.writeto_mem(self.ADDR,self.ADDR_MEM ,datetime)

