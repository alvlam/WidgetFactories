import sys
from random import randint
import pygame as pg
from functions import *
from gameglobals import *
from player import Player
from building import Building

# Initialize pg - in gameglobals

# Define the cloud object by extending pygame.sprite.Sprite
class Cloud(pg.sprite.Sprite):
    def __init__(self, loc=None):
        super(Cloud, self).__init__()

        self.image = load_image_file("cloud.png").convert_alpha()
        
        if loc is None:
            # The starting position is randomly generated
            self.rect = self.image.get_rect(
                center=(
                    randint(WORLD_WIDTH + 20, WORLD_WIDTH + 100),
                    randint(0, GROUND-100),
                )
            )
        else:
            self.rect = self.image.get_rect(center=(loc))

    # Move the cloud based on a constant speed
    # Remove the cloud when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-1, 0)
        if self.rect.right < 0:
            self.kill()

class Game(object):
    def __init__(self, screenSize):
        self.done = False
        self.screen = pg.display.set_mode(screenSize)
        pg.display.set_caption("Widget Factories!")
        self.clock = pg.time.Clock()
        self.fps = 60
        self.bgColour = pg.Color("gray5")
        
        # group to hold background clouds
        self.clouds = pg.sprite.Group()
        # Create initial random clouds and add to sprite groups
        i = 0
        while i < WORLD_WIDTH:
            newCloud = Cloud((i,randint(0, GROUND-100)))
            self.clouds.add(newCloud)
            ALL_SPRITES.add(newCloud, layer=0) # clouds = layer 0
            i += randint(200,400)

        # Create custom events for moving clouds, and adding a new cloud
        self.moveCloud = pg.USEREVENT + 1
        pg.time.set_timer(self.moveCloud, 3000)
        self.addCloud = pg.USEREVENT + 2
        pg.time.set_timer(self.addCloud, randint(30000,40000))

        # add buildings
        newShop = Building(SHOP_FILENAME, (WORLD_WIDTH//2,GROUND))
        BUILDINGS.add(newShop)
        ALL_SPRITES.add(newShop, layer=1) # buildings = layer 1

        # Set up players (with personal camera)
        self.players = pg.sprite.Group()

        if SINGLE_PLAYER:
            self.isSplitScreen = False
            self.player1 = Player(TRUCK_FILENAME, (50,GROUND), screenSize, P1_MAP, colour=pg.Color('sienna2'))
            self.players.add(self.player1)
            ALL_SPRITES.add(self.player1, layer=2) # players = layer 2
        else:
            self.isSplitScreen = True
            splitCamSize = (screenSize[0] // 2, screenSize[1])
            self.player1 = Player(TRUCK_FILENAME, (50,GROUND), splitCamSize, P1_MAP, colour=pg.Color('sienna2'))
            self.player2 = Player(TRUCK_FILENAME, (WORLD_WIDTH - 100,GROUND), splitCamSize, P2_MAP,
                        orientation="LEFT", colour=pg.Color('blue')) # player2 starts from right
            self.players.add(self.player1, self.player2, layer=2) # players = layer 2
            ALL_SPRITES.add(self.player1, self.player2, layer=2)
        
    # Run Main Loop
    def event_loop(self):
        # Look at every event in the queue
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True

            # Add a new cloud?
            elif event.type == self.addCloud:
                # Create the new cloud and add it to sprite groups
                newCloud = Cloud()
                self.clouds.add(newCloud)
                ALL_SPRITES.add(newCloud, layer=0) # layer 0

            elif event.type == self.moveCloud:
                self.clouds.update()
                
    def update(self, dt):

        # check pressed keys
        keys = pg.key.get_pressed()

        # q or escape to quit
        if keys[pg.K_ESCAPE]:
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
            if self.isSplitScreen and abs(self.player1.pos[0]+self.player1.image.get_width()//2-self.player2.pos[0]) <= SCREEN_WIDTH//2:
                self.isSplitScreen = False # players have come together
                #cam1 = (cam1[0]-self.screenSize[0]/2, cam1[1])
            elif abs(self.player1.pos[0]+self.player1.image.get_width()//2-self.player2.pos[0]) > SCREEN_WIDTH//2:
                self.isSplitScreen = True # players moved apart
        
        for b in BUILDINGS:
            b.update(self.players)

    def draw(self):
        # render world surface
        WORLD_SURFACE.fill(pg.Color("skyblue")) # fill to stop smearing
        pg.draw.rect(WORLD_SURFACE, pg.Color('darkgreen'), (0, GROUND, WORLD_WIDTH, WORLD_HEIGHT)) # grass
        pg.draw.line(WORLD_SURFACE, pg.Color('black'), (0, GROUND), (WORLD_WIDTH, GROUND), 5) # draw the ground floor
        
        ALL_SPRITES.draw(WORLD_SURFACE)

        # display speech bubbles for any messages
        for b in BUILDINGS:
            if b.message != "":
                b.say(b.message)
        
        for p in self.players:
            if p.message != "":
                p.say(p.message)

        # render player cameras
        self.screen.fill(self.bgColour)
        p1_view = WORLD_SURFACE.subsurface(self.player1.cam)
        self.screen.blit(p1_view, (0, 0))
        #pg.draw.rect(self.screen, pg.Color("darkgreen"), self.player1.screen_rect)
        
        if not SINGLE_PLAYER:
            p2_view = WORLD_SURFACE.subsurface(self.player2.cam)
            self.screen.blit(p2_view, (SCREEN_WIDTH // 2,0))
            #pg.draw.rect(self.screen, pg.Color("goldenrod"), self.player2.screen_rect)
            if self.isSplitScreen:
                pg.draw.line(self.screen, pg.Color("black"), (SCREEN_WIDTH // 2, 0),
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)


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
        self.screen = pg.display.set_mode(screenSize)
        pg.display.set_caption("Widget Factories!")
        #self.clock = pg.time.Clock()
        #self.fps = 60
        self.bgColour = pg.Color("black")
                    

if __name__ in "__main__":    
    game = Game((SCREEN_WIDTH, SCREEN_HEIGHT))
    game.run()
    pg.quit()
    sys.exit()
