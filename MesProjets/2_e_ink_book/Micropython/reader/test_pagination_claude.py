from pagination_claude import Reader

r = Reader("test.html", chars=30, lines=15)

print(r.pages)     # première page (list of str)

r.next()          # page suivante → r.pages[0]
print(r.pages)
r.prev()          # page précédente

#r.build(2)        # construit 2 pages → r.pages[0] et r.pages[1]

pos = r.save_position()
r.restore_position(pos)

for i in range(10):
    r.next()        
    print(r.pages,r.save_position())