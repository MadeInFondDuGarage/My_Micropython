#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 09:41:28 2021

@author: david
"""

def make_point(x, y):
    def point():
        print(f"Point({x}, {y})")
    def get_x():
        return x
    def get_y():
        return y
    def set_x(value):
        nonlocal x
        x = value
    def set_y(value):
        nonlocal y
        y = value
    # Attach getters and setters
    point.get_x = get_x
    point.set_x = set_x
    point.get_y = get_y
    point.set_y = set_y
    return point
    


point = make_point(1, 2)
point.get_x()
point()
point.set_x(42)
point()