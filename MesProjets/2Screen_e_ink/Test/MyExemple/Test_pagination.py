
import os,time
import pagination
import gc

#ensemble générique de variable

MyPagination= pagination.Pagination(max_char=30,max_ligne=20,page_return=4)
print(gc.mem_free())
#j'ouvre le fichier    
startime= time.ticks_ms()
f=open("test.html","r")
texte=""
#0,1784, 4463,7682
f.seek(4463)
for ligne in f:
    MyPagination.make_texte(ligne)
elapsed = time.ticks_diff(time.ticks_ms(), startime)

print("Temps moyen:", elapsed , "ms")
f.close()
print(gc.mem_free())

#j'attaque le découpage par zone
#startime= time.ticks_ms()

#pages=MyPagination.get_pages()

#elapsed = time.ticks_diff(time.ticks_ms(), startime)
#print("Temps moyen:", elapsed , "ms")
print(MyPagination.get_pages())
print(MyPagination.get_pos())


