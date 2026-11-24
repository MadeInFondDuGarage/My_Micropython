from RealTimeClock import RTC


def init_rtc_with_time():
    i2c_rtc=RTC()
    i2c_rtc.Set_AddrRtc(81,0x02)
    # a décommenter pour une mise a l'heure
    i2c_rtc.set_time(26,3,13,18,5,0)
    
def read_time():
    i2c_rtc=RTC()
    i2c_rtc.Set_AddrRtc(81,0x02)
    print(i2c_rtc.read_time())

def find_i2c_rtc():
    i2c_rtc=RTC()
    print(i2c_rtc.scan())
    
def timer_4_rtc():
    #interruption pour le rtc
    tim=Timer(1) # de 1 a 4 pour l'esp32
    tim.init(mode=Timer.PERIODIC, period=5000, callback=read_time) #create tim object,and init timer id = 2 , frequency = 2
    
if __name__ == "__main__":
    #init_rtc_with_time()
    find_i2c_rtc()
    read_time()
    