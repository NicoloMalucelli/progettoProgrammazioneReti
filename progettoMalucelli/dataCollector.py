# -*- coding: utf-8 -*-
"""
Created on Sun May 16 11:07:59 2021

@author: Nicolò
"""

from datetime import datetime
import random

def getTime():
    return datetime.now().strftime("%H:%M:%S")

def getTemperature():
    return random.randrange(16, 38, 1)

def getHumidity():
    return random.randrange(45, 80, 1)