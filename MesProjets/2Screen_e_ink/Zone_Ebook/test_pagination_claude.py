from pagination_claude_2 import Reader
import os,time

r = Reader("test.html", chars=30, lines=15,n_pages=1)

print(r.pages)     # première page (list of str)

r.next()          # page suivante → r.pages[0]
print(r.pages)
r.prev()          # page précédente

#r.build(2)        # construit 2 pages → r.pages[0] et r.pages[1]

pos = r.save_position()
r.restore_position(pos)

startime= time.ticks_ms()
for i in range(4):
    r.next()        
    print(r.pages,r.save_position())
    
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("Temps moyen:", elapsed , "ms")