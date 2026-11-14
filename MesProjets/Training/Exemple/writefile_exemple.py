import pyb
import os

print(os.uname()) 

print(os.getcwd()) 



try:
    os.mkdir("test") 
except:
    print("R茅pertoire existe")

print(os.listdir()) 

os.chdir("test") 
print(os.getcwd())

f=open("testfile.txt","w")
f.write("Test")
f.close()

print(os.listdir("/flash/test")) 

os.chdir("/flash") 
print(os.getcwd())

try :
    os.chdir("/sd") 
    print(os.getcwd())
    print(os.listdir("/sd"))
except:
    print("Carte SD absente")

try:
    os.mkdir("test") 
except:
    print("R鑼卲ertoire existe")

os.chdir("test") 
print(os.getcwd())


