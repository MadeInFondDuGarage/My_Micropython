import os

os.listdir('/')
log = open("/flash/log.csv", "w")
log.write("test")
log.close()
