
class Pagination():
    
    def __init__(self,max_char=30,max_ligne=20,page_return=2):
        self.max_char=max_char
        self.max_ligne=max_ligne
        self.page_return=page_return
        self.Texte=""
        self.page=[]
        self.pages=[]
        self.start=0
        self.end=self.max_char
        self.baliseOpen={
            "in_tag": False,
            "skip": None
        }
        self.ligne =""
        self.last_ligne=""

    def set_pagination(self,max_char=30,max_ligne=20,page_return=2):
        self.max_char=max_char
        self.max_ligne=max_ligne
        self.page_return=page_return

    def strip_html(self,line):
        result = []
        i = 0
        n = len(line)
        #line=line.strip(" ")
        
        while i < n:
            # zone à ignorer (script/style/head)
            if self.baliseOpen["skip"]:
                end = line.find('</' + self.baliseOpen["skip"], i)
                if end == -1:
                    return ''
                else:
                    i = line.find('>', end)
                    if i == -1:
                        return ''
                    i += 1
                    self.baliseOpen["skip"] = None

            # texte normal
            elif not self.baliseOpen["in_tag"]:
                start = line.find('<', i)

                if start == -1:
                    result.append(line[i:])
                    break

                if start > i:
                    result.append(line[i:start])

                i = start + 1
                self.baliseOpen["in_tag"] = True

            # lecture balise
            else:
                end = line.find('>', i)
                if end == -1:
                    return ''.join(result)

                tag = line[i:end].strip().lower()

                # --- gestion structure texte ---
                if tag.startswith('br'):
                    result.append('\n')

                elif tag.startswith('p'):
                    # nouveau paragraphe
                    if result and not result[-1].endswith('\n\n'):
                        result.append('\n\n')

                elif tag.startswith('/p'):
                    result.append('\n\n')

                # --- zones à ignorer ---
                elif tag.startswith('script'):
                    self.baliseOpen["skip"] = 'script'
                elif tag.startswith('style'):
                    self.baliseOpen["skip"] = 'style'
                elif tag.startswith('head'):
                    self.baliseOpen["skip"] = 'head'

                self.baliseOpen["in_tag"] = False
                i = end + 1
                
        return ''.join(result)
    
    def make_texte(self,ligne):
        clean=self.strip_html(ligne)
        if clean:
            self.Texte+=clean
            
    def make_pages(self, Texte):
        ligne =""
        #self.start=0
        #self.end=self.start+self.max_char
        lenTexte =len(Texte)

        for index in range(lenTexte):
            #je lance la lecture de la zone
            
            if self.end > lenTexte:
                self.end=lenTexte
            SoloLigne=Texte[self.start:self.end] #je construit la ligne simple
            saut=SoloLigne.find("\n",0)
            if saut > -1: #j'ai des saut de ligne je le reproduits dans la page
                self.end=self.start+saut
                saut=1
            #je test la fin de la ligne
            else:
                saut=0
                while self.end > self.start and Texte[self.end-1] not in (" ", "."):
                    self.end -= 1 #je reviens en arrière
            ligne+= Texte[self.start:self.end]    
            self.page.append(ligne.strip())    

            if len(self.page)>=self.max_ligne:
                self.pages.append(self.page)
                self.page=[]
            if len(self.pages)==self.page_return:
                return self.end
            
            self.start=self.end+saut
            self.end=self.start+self.max_char
            ligne=""
    
    def make_pages_test(self, Texte):
        cleanTexte=""
        NewTexte=self.strip_html(Texte) #ici je récupère le dernier morceau de ligne du cycle précédents
        if NewTexte:
            cleanTexte=self.last_ligne+NewTexte
        lenTexte =len(cleanTexte)
        start=0
        end=self.max_char

        if lenTexte>self.max_char:
            
            ligne_full=False

            for index in range(lenTexte):
                #je lance la lecture de la zone
                
                if end > lenTexte:
                    end=lenTexte
                    self.last_ligne=cleanTexte[start:]
                    return False

                SoloLigne=cleanTexte[start:end] #je construit la ligne simple
                saut=SoloLigne.find("\n",0)
                if saut > -1: #j'ai des sauts de ligne je le reproduits dans la page
                    end=start+saut
                    saut=1
                    ligne_full=True
                #je test la fin de la ligne
                else:
                    saut=0
                    if cleanTexte[end-1] in (" ", "."):
                        ligne_full=True
                    while end > start and cleanTexte[end-1] not in (" ", "."):
                        end -= 1 #je reviens en arrière
                        ligne_full=True

                if ligne_full: #si j'ai une ligne complete je l'ajoute et je reset, sinon je prend la suite ou au texte du tour suivant
                    self.ligne+= cleanTexte[start:end]    
                    self.page.append(self.ligne.strip()) 
                    self.ligne=""
                    ligne_full=False
                start=end+saut
                end=start+self.max_char
                
                
                if len(self.page)>=self.max_ligne:
                    self.pages.append(self.page)
                    self.page=[]
                if len(self.pages)==self.page_return:
                    return True
        else:
            #j'ai pas la bonne taille de texte alors je sort et j'ajoute a la sortie
            self.last_ligne=cleanTexte
            return False

    def get_texte(self):
        return self.Texte
    
    def set_pos(self,pos):
        self.start=pos
    
    def get_pos(self):
        return self.end
    
    def get_pages(self):
        pos=self.make_pages(self.Texte)
        return self.pages

    def get_pages_test(self):
        return self.pages
        
    def get_state(self):
        return self.baliseOpen

if __name__=="__main__":
    
    
    ligne= \
            '    <div class="c2">' \
            'This eBook is for the use of anyone anywhere in the United States and most'\
            'other parts of the world at no cost and with almost no restrictions'\
            'whatsoever. You may copy it, give it away or re-use it under the terms of'\
            'the Project Gutenberg License included with this eBook or online at'\
            '<a href="https://www.gutenberg.org">www.gutenberg.org</a>. If you are not'\
            'located in the United States, you will have to check the laws of the'\
            'country where you are located before using this eBook.'\
            '</div>'\
            'It is very seldom that mere ordinary people like John and myself secure'\
            'ancestral halls for the summer.'\
            '</p>'\
            '<p>'\
            'A colonial mansion, a hereditary estate, I would say a haunted house, and'\
            'reach the height of romantic felicity—but that would be asking too much of'\
            'fate!'\
            '</p>'\
            '<p>Still I will proudly declare that there is something queer about it.</p>'\
            '<p>'\
            'Else, why should it be let so cheaply? And why have stood so long'\
            'untenanted?'\
            '</p>'\
            '<p>John laughs at me, of course, but one expects that in marriage.</p>'\
            '<p>'\
            'John is practical in the extreme. He has no patience with faith, an'\
            'intense horror of superstition, and he scoffs openly at any talk of things'\
            'not to be felt and seen and put down in figures.'\
            '</p>'\
            '<p>'\
            'John is a physician, and <i>perhaps</i>—(I would not say it to a living   '\
            'soul, of course, but this is dead paper and a great relief to my mind)—<i'\
            '>perhaps</i'\
            '>'\
            'that is one reason I do not get well faster.'\
            '</p>'\
            '<p>You see, he does not believe I am sick!</p>'\
            '<p>And what can one do?</p>'\
            '<p>'\
            'If a physician of high standing, and one’s own husband, assures friends'\
            'and relatives that there is really nothing the matter with one but'\
            'temporary nervous depression—a slight hysterical tendency—what is one to'\
            'do?'\
            '</p>'\
            '<p>'\
            'My brother is also a physician, and also of high standing, and he says the'\
            'same thing.'\
            '</p>'\
        
    MyPagination= Pagination(max_char=30,max_ligne=20,page_return=2)
    MyPagination.make_texte(ligne)
    #print(MyPagination.get_texte())
    #print(MyPagination.get_pages())
    for i in range(len(ligne)):
        start=i*30
        end=start+30
        state=MyPagination.make_pages_test(ligne[start:end])
        if state:
            break
    print(MyPagination.get_pages_test())