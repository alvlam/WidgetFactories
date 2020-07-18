import sys
import pygame as pg
from functions import *
from gameglobals import *
from player import Player
from building import Building

# Initialize pg - in gameglobals

class Game(object):
    def __init__(self, screenSize):
        self.done = False
        self.screenSize = screenSize
        self.screen = pg.display.set_mode(screenSize)
        pg.display.set_caption("Widget Factories!")
        self.clock = pg.time.Clock()
        self.fps = 60
        self.bgColour = pg.Color("gray5")

        # Set up players (with personal camera)
        # separate group for rendering
        self.players = pg.sprite.Group()

        if SINGLE_PLAYER:
            self.isSplitScreen = False
            self.player1 = Player(TRUCK_FILENAME, (50,GROUND), self.screenSize, P1_MAP, colour=pg.Color('sienna2'))
            self.players.add(self.player1)
        else:
            self.isSplitScreen = True
            splitCamSize = (self.screenSize[0] // 2, self.screenSize[1])
            self.player1 = Player(TRUCK_FILENAME, (50,GROUND), splitCamSize, P1_MAP, colour=pg.Color('sienna2'))
            self.player2 = Player(TRUCK_FILENAME, (WORLD_WIDTH - 100,GROUND), splitCamSize, P2_MAP,
                        orientation="LEFT", colour=pg.Color('blue')) # player2 starts from right
            self.players.add(self.player1, self.player2)
        
        
#        BUILDINGS.add(Building(SHOP_FILENAME, (600,GROUND)))
        BUILDINGS.add(Building(SHOP_FILENAME, (1200,GROUND)))

#        self.buildings.add(Building(IMG_FACTORY, (200,GROUND)))
#        self.buildings.add(Building(IMG_FACTORY, (WORLD_WIDTH - IMG_FACTORY.get_width() - 200,GROUND)))

    
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
            if self.isSplitScreen and abs(self.player1.pos[0]+self.player1.image.get_width()/2-self.player2.pos[0]) <= self.screenSize[0]/2:
                self.isSplitScreen = False # players have come together
                #cam1 = (cam1[0]-self.screenSize[0]/2, cam1[1])
            elif abs(self.player1.pos[0]+self.player1.image.get_width()/2-self.player2.pos[0]) > self.screenSize[0]/2:
                self.isSplitScreen = True # players moved apart
        
        for b in BUILDINGS:
            b.update(self.players)

    def draw(self):
        # render world surface
        WORLD_SURFACE.fill(pg.Color("skyblue")) # fill to stop smearing
        pg.draw.rect(WORLD_SURFACE, pg.Color('darkgreen'), (0, GROUND, WORLD_WIDTH, WORLD_HEIGHT)) # grass
        pg.draw.line(WORLD_SURFACE, pg.Color('black'), (0, GROUND), (WORLD_WIDTH, GROUND), 5) # draw the ground floor
        BUILDINGS.draw(WORLD_SURFACE)
        self.players.draw(WORLD_SURFACE)

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
