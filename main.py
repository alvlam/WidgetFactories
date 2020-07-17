import sys
from os import path
import pygame as pg

SINGLE_PLAYER = True # TO DO: make this selectable via menu

p1_map = {
        pg.K_a: ("move", (-1, 0)),
        pg.K_d: ("move", (1, 0)),
        pg.K_w: ("speed", 1),
        pg.K_s: ("speed", -1)}
p2_map = {
        pg.K_LEFT: ("move", (-1, 0)),
        pg.K_RIGHT: ("move", (1, 0)),
        pg.K_UP: ("speed", 1),
        pg.K_DOWN: ("speed", -1)}

# Initialize pg
pg.init()

#------ Function definitions ------------------------------

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

#------ Sprite definitions ------------------------------
class Player(pg.sprite.Sprite):
    def __init__(self, img, loc, camSize, control_map, speed=2, orientation="RIGHT", colour=None):
        pg.sprite.Sprite.__init__(self)
        
        self.image = load_image_file(img)
        self.rect = self.image.get_rect()

        # trying colourisation via blend
        if colour is not None:
            colourImage = pg.Surface(self.image.get_size()).convert_alpha()
            colourImage.fill(colour)
            self.image.blit(colourImage, (0,0), special_flags = pg.BLEND_RGBA_MULT)

        #self.mask = pg.mask.from_surface(self.image)

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

        for control in self.controls:
            if keys[control]:
                if self.controls[control][0] == "move":
                    #self.rect.move_ip(self.controls[control][1])
                    self.move(self.controls[control][1])
                if self.controls[control][0] == "speed":
                    self.changeSpeed(self.controls[control][1])

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

class Building(pg.sprite.Sprite):
    def __init__(self, img, loc):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        location = (loc[0], loc[1] - self.image.get_height()) # centery off the ground
        self.rect.topleft = location
    
    # draw text box above building
    def say(self, text, surf):
        aboveBuilding = (self.rect.center[0], self.rect.center[1]-100)
        draw_text_box(surf, text, FONT_ARIAL, pg.Color('black'), False, aboveBuilding)

class Game(object):
    def __init__(self, screenSize):
        self.done = False
        self.screenSize = screenSize
        self.screen = pg.display.set_mode(screenSize)
        pg.display.set_caption("Widget Factories!")
        self.clock = pg.time.Clock()
        self.fps = 60
        self.bgColour = pg.Color("gray5")
        
        # Set up world surface
        global WORLD_WIDTH, WORLD_HEIGHT # global for camera edge checks
        WORLD_WIDTH = 2000
        WORLD_HEIGHT = 400
        self.worldSurface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
        self.ground = self.worldSurface.get_height() - 100 # ground height

        # Set up players (with personal camera)
        # separate group for rendering
        self.players = pg.sprite.Group()

        truck_filename = "truck64px.png"

        if SINGLE_PLAYER:
            self.isSplitScreen = False
            self.player1 = Player(truck_filename, (50,self.ground), self.screenSize, p1_map, colour=pg.Color('sienna2'))
            self.players.add(self.player1)
        else:
            self.isSplitScreen = True
            splitCamSize = (self.screenSize[0] // 2, self.screenSize[1])
            self.player1 = Player(truck_filename, (50,self.ground), splitCamSize, p1_map, colour=pg.Color('sienna2'))
            self.player2 = Player(truck_filename, (WORLD_WIDTH - 100,self.ground), splitCamSize, p2_map,
                        orientation="LEFT", colour=pg.Color('blue')) # player2 starts from right
            self.players.add(self.player1, self.player2)
        
        # Set up buildings
        global IMG_FACTORY, IMG_SHOP
        # Icons made by https://www.flaticon.com/authors/nhor-phai
        IMG_FACTORY = load_image_file("factory512px.png", (128,128))
        IMG_SHOP = load_image_file("shop512px.png", (128,128))
        
        # Create buildings and add to group for rendering
        self.buildings = pg.sprite.Group()
        self.buildings.add(Building(IMG_FACTORY, (200,self.ground)))
        self.buildings.add(Building(IMG_SHOP, (600,self.ground)))
        self.buildings.add(Building(IMG_SHOP, (1200,self.ground)))
        self.buildings.add(Building(IMG_FACTORY, (WORLD_WIDTH - IMG_FACTORY.get_width() - 200,self.ground)))

        # pre-load font
        global FONT_ARIAL
        FONT_ARIAL = pg.font.SysFont('Arial', 18)
    
    # Run Main Loop
    def event_loop(self):
        # Look at every event in the queue
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                
    def update(self, dt):

        # check pressed keys
        keys = pg.key.get_pressed()

        # q or escape to quit
        if keys[pg.K_ESCAPE] or keys[pg.K_q]:
            self.done = True

        for p in self.players.sprites():
            p.update(keys)
        
        # checking pressed mouse and move the player around
        #click = pg.mouse.get_pressed()
        #if click[0] == True: # evaluate left button
        #    player1.setTarget(pg.mouse.get_pos())

        # update split/joint screen
        #if isSplitScreen and (cam1[0]+self.screenSize[0]/2 >= cam2[0]):
        if not SINGLE_PLAYER:
            if self.isSplitScreen and abs(self.player1.pos[0]+self.player1.image.get_width()/2-self.player2.pos[0]) <= self.screenSize[0]/2:
                self.isSplitScreen = False # players have come together
                #cam1 = (cam1[0]-self.screenSize[0]/2, cam1[1])
            elif abs(self.player1.pos[0]+self.player1.image.get_width()/2-self.player2.pos[0]) > self.screenSize[0]/2:
                self.isSplitScreen = True # players moved apart
        
    def draw(self):
        # render world surface
        self.worldSurface.fill(pg.Color("skyblue")) # fill to stop smearing
        pg.draw.rect(self.worldSurface, pg.Color('darkgreen'), (0, self.ground, WORLD_WIDTH, WORLD_HEIGHT)) # grass
        pg.draw.line(self.worldSurface, pg.Color('black'), (0, self.ground), (WORLD_WIDTH, self.ground), 5) # draw the ground floor
        self.buildings.draw(self.worldSurface)
        self.players.draw(self.worldSurface)

        # Check if players have collided with buildings
        for player in self.players:
            collided_buildings = pg.sprite.spritecollide(player, self.buildings, False)
            for building in collided_buildings:
                # If so, then factory should say hello
                building.say('Hello!', self.worldSurface)

        # render player cameras
        self.screen.fill(self.bgColour)
        p1_view = self.worldSurface.subsurface(self.player1.cam)
        self.screen.blit(p1_view, (0, 0))
        #pg.draw.rect(self.screen, pg.Color("darkgreen"), self.player1.screen_rect)
        
        if not SINGLE_PLAYER:
            p2_view = self.worldSurface.subsurface(self.player2.cam)
            self.screen.blit(p2_view, (self.screenSize[0] // 2,0))
            #pg.draw.rect(self.screen, pg.Color("goldenrod"), self.player2.screen_rect)
            if self.isSplitScreen:
                pg.draw.line(self.screen, pg.Color("black"), (self.screenSize[0] // 2, 0),
                        (self.screenSize[0] // 2, self.screenSize[1]), 2)


        # Render world to gameDisplay, at current camera position
        #gameDisplay.fill(pg.Color('white')) # fill the background pg.Color('white') to avoid smearing
        #if isSplitScreen: # show each player centepg.Color('red') in own cam
        #    gameDisplay.blit(world, (0,0), pg.Rect(cam1[0],cam1[1],int(DISPLAY_WIDTH/2),DISPLAY_HEIGHT))
        #    gameDisplay.blit(world, (DISPLAY_WIDTH/2,0), pg.Rect(cam2[0],cam2[1],int(DISPLAY_WIDTH/2),DISPLAY_HEIGHT))
        #    pg.draw.line(gameDisplay, pg.Color('black'), (int(DISPLAY_WIDTH/2), 0), (int(DISPLAY_WIDTH/2), DISPLAY_HEIGHT), 10)
        #else: # show both players in wide cam, based on cam1 location
        #    gameDisplay.blit(world, (0,0), pg.Rect(cam1[0],cam1[1],DISPLAY_WIDTH,DISPLAY_HEIGHT))
        
        #draw_text_box(gameDisplay, "player1: "+str(player1.rect)+" | cam1: "+str(cam1), FONT_ARIAL, pg.Color('black'), False, (int(DISPLAY_WIDTH/2), 20))

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pg.display.update()

# to be completed - select 1 or 2 player, press return to start
class Menu(object):
    def __init__(self, screenSize):
        self.done = False
        self.screenSize = screenSize
        self.screen = pg.display.set_mode(screenSize)
        pg.display.set_caption("Widget Factories!")
        #self.clock = pg.time.Clock()
        #self.fps = 60
        self.bgColour = pg.Color("black")
                    

if __name__ in "__main__":
    game = Game((800, 400))
    game.run()
    pg.quit()
    sys.exit()
