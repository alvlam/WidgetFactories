import pygame as pg
from os import path
from gameglobals import *

# Function to load image file and optional resize
def load_image_file(fileName, resize=None):
    img = pg.image.load(path.join(path.dirname(__file__), fileName))
    if resize is not None:
        img = pg.transform.scale(img, resize)
    return img

# Function to draw a text box
# based on https://stackoverflow.com/questions/60997970/how-to-add-a-text-speech-in-pg
def draw_text_box(surf, text, font, color, bold, loc):
    font.set_bold(bold)
    textSurf = font.render(text, True, color, pg.Color('white')).convert_alpha()
    textSize = textSurf.get_size()   
    bubbleSurf = pg.Surface((textSize[0]*2, textSize[1]*2))
    bubbleSurf.fill(pg.Color('white'))
    bubbleRect = bubbleSurf.get_rect()
    pg.draw.rect(bubbleSurf, color, bubbleRect, 3)
    bubbleSurf.blit(textSurf, textSurf.get_rect(center = bubbleRect.center))
    bubbleRect.center = loc
    surf.blit(bubbleSurf, bubbleRect) # render to surf
