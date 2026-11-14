import time
import machine
import onewire, ds18x20

# the device is on GPIO12
dat = machine.Pin('X7')

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# loop 10 times and print all temperatures
while True:
    print('temperatures:', end=' ')
    ds.convert_temp()
    time.sleep_ms(750)
 #   for rom in roms:
  #      print(ds.read_temp(rom), end=' ')
    print(ds.read_temp(roms[0]))
    print()