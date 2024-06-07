import time
import datetime
import json
import os
import pygame
import pickle
import pygetwindow as gw
from pynput import keyboard, mouse
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import threading
import time
import sys

#---------------
INACTIVE_TIME = 15  # durée avant de considérer l'utilisateur comme inactif
#---------------
STOCKAGE_FILE = "activity_log.json"
MONTHS = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Jui", "Août", "Sept", "Oct", "Nov", "Dec"]
START_TIME = None

#PYGAME -------------------------
CLOCK = pygame.time.Clock()
SCREEN_WIDTH, SCREEN_HEIGHT = 760, 160
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FONT_LILITAONE_50 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 50)
FONT_LILITAONE_30 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 30)
FONT_LILITAONE_10 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 10)
CLR_WHITE = (255,255,255)
CLR_BLACK = (0,0,0)