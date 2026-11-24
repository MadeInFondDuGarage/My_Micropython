import os, vfs, esp32
# Nom de la partition comme dans partitions.csv

bdev = esp32.Partition("vfs")

# Formater
#vfs.VfsFat.mkfs(bdev)

# Monter dans /data
os.mount(bdev, "/")

#f=open("/data/test.txt","w")
#f.write("""Ceci est un fichier de test""")
#f.close()

# Vérifier
os.listdir("/")