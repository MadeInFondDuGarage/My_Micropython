#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 22:19:02 2021

@author: david
"""

user="Jason"

def check_user(username):
    def deco(func):
        def wrapper():
            if username== "Jason":
                print('ok user granted')
                return func()
            else:
                print('non autoriser')
        return wrapper
    return deco
        
@check_user('Jason')
def infos_user():
    print("hello")
    
infos_user()