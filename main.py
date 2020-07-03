from os import path
import pygame

# Initialize pygame
pygame.init()

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

#------ Function definitions ------------------------------

# Function to load image file and optional resize
def load_image_file(fileName, resize=None):
    img = pygame.image.load(path.join(path.dirname(__file__), fileName))
    if resize is not None:
        img = pygame.transform.scale(img, resize)
    return img

# Function to draw a text box
# based on https://stackoverflow.com/questions/60997970/how-to-add-a-text-speech-in-pygame
def draw_text_box(surf, text, font, color, bold : bool, loc):
    font.set_bold(bold)
    textSurf = font.render(text, True, color, WHITE).convert_alpha()
    textSize = textSurf.get_size()   
    bubbleSurf = pygame.Surface((textSize[0]*2, textSize[1]*2))
    bubbleRect = bubbleSurf.get_rect()
    pygame.draw.rect(bubbleSurf, color, bubbleRect, 3)
    bubbleSurf.blit(textSurf, textSurf.get_rect(center = bubbleRect.center))
    bubbleRect.center = loc
    surf.blit(bubbleSurf, bubbleRect) # render to surf

#------ Sprite definitions ------------------------------
class Truck(pygame.sprite.Sprite):
    def __init__(self, img, locX=0, speed=2, orientation="RIGHT"):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.orientation = "RIGHT" # source image is facing right
        self.setDirection(orientation)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
        self.pos = pygame.math.Vector2(location)
        self.setTarget(self.pos)
        self.speed = speed
    
        self.autoMoving = False

    def setDirection(self, direction):
        if direction.upper() == "LEFT":
            if self.orientation == "RIGHT":
              self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = "LEFT"
        else:
            if self.orientation == "LEFT":
              self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = "RIGHT"
    
    def setTarget(self, pos):
        if pos[0] > 0 and pos[0] < WORLD_WIDTH: #and pos[1] > 0 and pos[1] < DISPLAY_HEIGHT:
            # set orientation and flip image if necessary
            if pos[0] < self.pos[0]:
              self.setDirection("LEFT")
            elif pos[0] > self.pos[0]:
              self.setDirection("RIGHT")
            self.target = pygame.math.Vector2((pos[0], self.pos[1]))
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
        
    def update(self, cam):
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

        if (self.pos[0] > (DISPLAY_WIDTH/2)) \
            and (self.pos[0] < (WORLD_WIDTH - DISPLAY_WIDTH/2)): # player is away from edges of world
            return (int(self.pos[0] - DISPLAY_WIDTH/2), cam[1]) # keep camera centered on player
        else:
            return cam

class Building(pygame.sprite.Sprite):
    def __init__(self, img, locX=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
    
    # draw text box above building
    def say(self, text : str):
        aboveBuilding = (self.rect.center[0], self.rect.center[1]-100)
        draw_text_box(world, text, FONT_ARIAL, BLACK, False, aboveBuilding)


def Main(gameDisplay, clock):

    # Set up world surface and camera pos
    global world
    world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)) # Create world surface
    camera = (0,0) # Create Camara Starting Position (center of display)
    
    # Create buildings and add to group for rendering
    buildings = pygame.sprite.Group()
    buildings.add(Building(IMG_FACTORY, 200))
    buildings.add(Building(IMG_SHOP, 600))
    buildings.add(Building(IMG_SHOP, 1200))
    buildings.add(Building(IMG_FACTORY, WORLD_WIDTH - IMG_FACTORY.get_width() - 200))

    # Create the players
    player1 = Truck(IMG_TRUCK, 50)
    player2 = Truck(IMG_TRUCK, DISPLAY_WIDTH - IMG_TRUCK.get_width() - 50, orientation="LEFT") # player2 starts from right
    # add to separate group for rendering
    players = pygame.sprite.Group()
    players.add(player1, player2)

    done = False

    # Main loop
    while not done:
        clock.tick(FPS)

        # Look at every event in the queue
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()

        # check pressed keys
        keys = pygame.key.get_pressed()

        # q or escape to quit
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            pygame.quit()

        # player1: left and right to move
        if keys[pygame.K_a]: # left
            player1.move((-1,0))
        elif keys[pygame.K_d]: # right
            player1.move((1,0))

        # player1: W and S to change speed
        if keys[pygame.K_w]:
            player1.changeSpeed(1)
        elif keys[pygame.K_s]:
            player1.changeSpeed(-1)

        # player2: left and right to move
        if keys[pygame.K_LEFT]:
            player2.move((-1,0))
        elif keys[pygame.K_RIGHT]:
            player2.move((1,0))
        
        # player2: up and down to change speed
        if keys[pygame.K_UP]:
            player2.changeSpeed(1)
        elif keys[pygame.K_DOWN]:
            player2.changeSpeed(-1)
        
        # checking pressed mouse and move the player around
        click = pygame.mouse.get_pressed()
        if click[0] == True: # evaluate left button
            player1.setTarget(pygame.mouse.get_pos())
        
        # Updates
        camera = player1.update(camera) # update player1 and camera_pos
        player2.update(camera) # update player2 and camera_pos

        # render to world surface
        world.fill(WHITE)
        pygame.draw.line(world, BLACK, (0, GROUND), (WORLD_WIDTH, GROUND), 5) # draw the ground
        buildings.draw(world)
        players.draw(world)

        # Check if players have collided with buildings
        for player in players:
            collided_buildings = pygame.sprite.spritecollide(player, buildings, False)
            for building in collided_buildings:
                # If so, then factory should say hello
                building.say('Hello!')

        # Render world to gameDisplay, at current camera position
        gameDisplay.fill(WHITE) # fill the background white to avoid smearing
        gameDisplay.blit(world, (0,0), pygame.Rect(camera[0],camera[1],DISPLAY_WIDTH,DISPLAY_HEIGHT))
        
        draw_text_box(gameDisplay, "camera: "+str(camera), FONT_ARIAL, BLACK, False, (int(DISPLAY_WIDTH/2), 20))

        # Update the display
        pygame.display.flip()

    pygame.quit()
    quit()


if __name__ in "__main__":
    
    # Define globals
    global FPS # for clock
    FPS = 60

    global WHITE, RED, GREEN, BLUE, BLACK # colours
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)

    global DISPLAY_WIDTH, DISPLAY_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT # screen and world sizes
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 400
    WORLD_WIDTH = 2000
    WORLD_HEIGHT = 400

    global GROUND
    GROUND = DISPLAY_HEIGHT-100 # ground height

    # Load everthing
    global IMG_FACTORY, IMG_SHOP, IMG_TRUCK
    # Icons made by https://www.flaticon.com/authors/nhor-phai
    IMG_FACTORY = load_image_file("factory512px.png", (128,128))
    IMG_SHOP = load_image_file("shop512px.png", (128,128))
    IMG_TRUCK = load_image_file("truck64px.png")

    global FONT_ARIAL
    FONT_ARIAL = pygame.font.SysFont('Arial', 18)

    gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Silly Inventions!")
    clock = pygame.time.Clock()

    # Run Main Loop
    Main(gameDisplay, clock)
