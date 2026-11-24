import os

def init_sd():
    try:
        from machine import Pin, SPI, SDCard

        # Configuration SPI avec tes pins
        spi = SPI(1,
                  baudrate=20000000,
                  polarity=0,
                  phase=0,
                  sck=Pin(1),
                  mosi=Pin(16),
                  miso=Pin(15))

        cs = Pin(42, Pin.OUT)

        # Init SD
        sd = SDCard(slot=1, spi=spi, cs=cs)

        # Montage
        os.mount(sd, "/sd")

        print("✅ SD montée")

        return True

    except Exception as e:
        print("❌ SD absente / erreur :", e)
        return False


def list_dirs(path="/sd"):
    dirs = []
    try:
        for name in os.listdir(path):
            full = path + "/" + name
            try:
                if os.stat(full)[0] & 0x4000:
                    dirs.append(name)
            except:
                pass
    except Exception as e:
        print("Erreur lecture :", e)

    return dirs


# --- MAIN ---

if init_sd():
    d = list_dirs()

    print("📁 Répertoires :")
    for x in d:
        print(" -", x)
else:
    print("⚠️ Carte non détectée")