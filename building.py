import pygame as pg
import functions as fn
from gameglobals import *

class Building(pg.sprite.Sprite):
    def __init__(self, img, loc):
        super(Building, self).__init__()
        
        self.image = (fn.load_image_file(img, (128,128))).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        location = (loc[0]- self.image.get_width()//2, loc[1] - self.image.get_height()) # centerx and place on the ground
        self.rect.topleft = location
    
        # message, for speech bubble
        self.message = ""

    def update(self, players):
        self.message = "" # clear any previous message

        # Check if players have collided with buildings
        for player in players:
            if self.rect.colliderect(player):
                self.message = 'Hello!'
            else:
                self.message = ""

    # draw text box above building
    def say(self, text):
        aboveBuilding = (self.rect.center[0], self.rect.center[1]-100)
        fn.draw_text_box(WORLD_SURFACE, text, FONT_ARIAL, pg.Color('black'), False, aboveBuilding)
