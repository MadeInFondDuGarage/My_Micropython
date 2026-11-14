import time
import machine
import onewire, ds18x20

# the device is on GPIO12
dat = machine.Pin(27)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# loop 10 times and print all temperatures
while True:
    print('temperatures:', end=' ')
    try:
        ds.convert_temp()
    except:
        print('erreur de connection')
    time.sleep_ms(750)
 #   for rom in roms:
  #      print(ds.read_temp(rom), end=' ')
    try:
        temp=ds.read_temp(roms[0])
    except:
        temp=0
        print('error')
    print(temp)
