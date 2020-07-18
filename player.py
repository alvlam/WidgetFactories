import pygame as pg
import functions as fn
from gameglobals import *
from building import Building

class Player(pg.sprite.Sprite):
    def __init__(self, img, loc, camSize, control_map, speed=2, orientation="RIGHT", colour=None):
        pg.sprite.Sprite.__init__(self)
        
        self.image = fn.load_image_file(img)
        self.rect = self.image.get_rect()

        # trying colourisation via blend
        if colour is not None:
            colourImage = pg.Surface(self.image.get_size()).convert_alpha()
            colourImage.fill(colour)
            self.image.blit(colourImage, (0,0), special_flags = pg.BLEND_RGBA_MULT)

        #self.mask = pg.mask.from_surface(self.image)

        # message, for speech bubble
        self.message = ""

        # camera settings
        self.orientation = "RIGHT" # source image is facing right
        self.setDirection(orientation)
        self.rect.center = (loc[0], loc[1]-self.rect.height) # centery off the ground
        self.pos = pg.math.Vector2(self.rect.center)
        self.setTarget(self.pos)
        self.speed = speed
        self.controls = control_map
        self.autoMoving = False

        # split screen camera
        self.cam = pg.Rect(0, 0, camSize[0], camSize[1])
        self.updateCam() # center cam on player position, adjusting for edges

    def setDirection(self, direction):
        if direction.upper() == "LEFT":
            if self.orientation == "RIGHT":
              self.image = pg.transform.flip(self.image, True, False)
            self.orientation = "LEFT"
        else:
            if self.orientation == "LEFT":
              self.image = pg.transform.flip(self.image, True, False)
            self.orientation = "RIGHT"
    
    def setTarget(self, pos):
        if pos[0] > 0 and pos[0] < (WORLD_WIDTH - self.image.get_width()): #and pos[1] > 0 and pos[1] < DISPLAY_HEIGHT:
            # set orientation and flip image if necessary
            if pos[0] < self.pos[0]:
              self.setDirection("LEFT")
            elif pos[0] > self.pos[0]:
              self.setDirection("RIGHT")
            self.target = pg.math.Vector2((pos[0], self.pos[1]))
        else:
            self.target = self.pos
    
    def move(self, vector):
      # set orientation and flip image if necessary
      if vector[0] < 0:
        self.setDirection("LEFT")
      else:
        self.setDirection("RIGHT")
      self.setTarget((self.rect.left+(vector[0]*self.speed),self.rect.top+(vector[1]*self.speed)))
    
    def changeSpeed(self, delta):
        if delta < 0 and self.speed > 1:
            self.speed += delta
        elif delta > 0 and self.speed <= 10: # change to MAX_SPEED
            self.speed += delta
        
    def update(self, keys):

        self.message = "" # clear any previous message

        for control in self.controls:
            if keys[control]:
                if self.controls[control][0] == "move":
                    #self.rect.move_ip(self.controls[control][1])
                    self.move(self.controls[control][1])
                if self.controls[control][0] == "speed":
                    self.changeSpeed(self.controls[control][1])
                if self.controls[control][0] == "place":
                    newBuilding = Building(FACTORY_FILENAME, (self.rect.centerx, GROUND))
                    # check if there is room to place new factory
                    if pg.sprite.spritecollide(newBuilding, BUILDINGS, False):
                        self.message = "No room!"
                    else:
                        BUILDINGS.add(newBuilding)

        vector = self.target - self.pos
        move_length = vector.length()

        if move_length < self.speed:
            self.pos = self.target
            self.autoMoving = False
        elif move_length != 0:
            vector.normalize_ip()
            vector = vector * self.speed
            self.pos += vector
        else:
            self.autoMoving = False

        self.rect.topleft = list(int(v) for v in self.pos)

        self.updateCam()

    # update player camera
    def updateCam(self):
        self.cam.center = self.rect.center
        # adjust for edges
        self.cam.left = 0 if self.cam.left < 0 else self.cam.left
        self.cam.top = 0 if self.cam.top < 0 else self.cam.top
        self.cam.left = WORLD_WIDTH-self.cam.width if self.cam.right > WORLD_WIDTH else self.cam.left
        self.cam.top = WORLD_HEIGHT-self.cam.height if self.cam.bottom > WORLD_HEIGHT else self.cam.top

        #if split:
        #    if (self.pos[0] + self.image.get_width()/2 >= (DISPLAY_WIDTH/4)) \
        #        and (self.pos[0] + self.image.get_width()/2 <= (WORLD_WIDTH - DISPLAY_WIDTH/4)): # player is away from edges of world
        #        return (int(self.pos[0] + self.image.get_width()/2 - DISPLAY_WIDTH/4), cam[1]) # keep camera centered on player
        #    elif (self.pos[0] < (DISPLAY_WIDTH/4)): # is at left side of world
        #        return (0,0)
        #    else: # is at right side of world
        #        return (WORLD_WIDTH - DISPLAY_WIDTH/2, cam[1])
        #else: # not split
        #    if (self.pos[0] + self.image.get_width()/2 >= (DISPLAY_WIDTH/4)) \
        #        and (self.pos[0] + self.image.get_width()/2 <= (WORLD_WIDTH - 3*DISPLAY_WIDTH/4)): # player is away from edges of world
        #        return (int(self.pos[0] + self.image.get_width()/2 - DISPLAY_WIDTH/4), cam[1]) # keep camera centered on player
        #    elif (self.pos[0] < (DISPLAY_WIDTH/4)): # is at left side of world
        #        return (0,0)
        #    else: # is at right side of world
        #        return (WORLD_WIDTH - DISPLAY_WIDTH, cam[1])

    # draw text box above player
    def say(self, text):
        abovePlayer = (self.rect.center[0], self.rect.center[1]-100)
        fn.draw_text_box(WORLD_SURFACE, text, FONT_ARIAL, pg.Color('black'), False, abovePlayer)
        