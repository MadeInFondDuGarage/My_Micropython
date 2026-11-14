import uasyncio
from time import sleep_ms

async def blink(led, period_ms):
    while True:
        led.on()
        await uasyncio.sleep_ms(period_ms)
        led.off()
        await uasyncio.sleep_ms(period_ms)
        
async def printit():
    for i in range(20):
        await uasyncio.sleep_ms(500)
        print(f"{i} blink")
    print("end printit")

async def autostop():
    await uasyncio.sleep_ms(20000)
    loop.stop()
    
# async def main(led1):
#     uasyncio.create_task(blink(led1, 100))
#     uasyncio.create_task(printit())
#     await uasyncio.sleep_ms(10000)

# Running on a generic board
from machine import Pin
print("async")
led=Pin(2,Pin.OUT)
#uasyncio.run(main(led))

loop=uasyncio.get_event_loop()
loop.create_task(blink(led, 100))
loop.create_task(printit())
loop.create_task(autostop())
loop.run_forever()


