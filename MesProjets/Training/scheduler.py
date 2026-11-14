import schedule
import time

def job():
    print("I'm working...")
    
def  secondes():
    print('les secondes aussi')
    

#schedule.every(1).minutes.do(job)
schedule.every(10).seconds.do(secondes)



x=0
while True:
    schedule.run_pending()
    time.sleep(1)
    print(x)
    x+=1