#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 10:26:34 2021

@author: david
"""

#simple class

class debit:
    
    def __init__(self,in_connexion,_valeur,out_connexion):
        self._in_connexion=in_connexion
        self._valeur=_valeur
        self._out_connexion=out_connexion
    
    def set_in(self,valeur):
        self._in_connexion=valeur
        
    def get_in(self):
        return self._in_connexion
    
    
class Employee: #permet de creer un pseudo strucure de donnée mais ne suporte pas le multi instance. préférer un dict, ou alors creer un __init__
    pass

john = Employee()  # Create an empty employee record

# Fill the fields of the record
john.name = 'John Doe'
john.dept = 'computer lab'
john.salary = 1000

class Reverse:
    """Iterator for looping over a sequence backwards."""
    def __init__(self, data):
        self.data = data
        self.index = len(data)

    def __iter__(self):#dans une class si on a une definition du __next__ le iter permet de renvoyer directement au next et d'utiliser la class dans un for ligne in lignes:
        return self

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]