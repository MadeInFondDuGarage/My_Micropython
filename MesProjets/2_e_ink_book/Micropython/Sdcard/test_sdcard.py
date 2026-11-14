from sdcard import  SDCard
import os

def test_sdcard():
    try:
        spi=SPI(1, sck=Pin(SD_SCLK), mosi=Pin(SD_MOSI),miso=Pin(SD_MISO))
        sd=SDCard(spi, Pin(SD_CS))
        vfs = os.VfsFat(sd)
        os.mount(vfs,'/sd')
        print("Carte SD montée avec succès")
        f=open("/sd/test.txt","w")
        f.write("""Ceci est un fichier de test""")
        f.close()
        os.listdir('/sd')
        print("test d'écriture réussi")
        f=open("/sd/test.txt","r")
        contenu=f.read()
        print(contenu)
        os.umount('/sd') #ne pas oublier de quitter
    except Exception as e:
        print("Erreur:", e)
        
if __name__=="__main__":
    test_sdcard()