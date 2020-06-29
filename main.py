from os import path
import pygame

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

# Define globals
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 400

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GROUND = DISPLAY_HEIGHT-100

# Function to load image file and optional resize
def load_image_file(fileName, resize=None):
    img = pygame.image.load(path.join(path.dirname(__file__), fileName))
    if resize is not None:
        img = pygame.transform.scale(img, resize)
    return img

#------ Sprite definitions ------------------------------
class Truck(pygame.sprite.Sprite):
    def __init__(self, locX=0, speed=2, orientation="RIGHT"):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMG_TRUCK
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.orientation = "RIGHT" # source image is facing right
        self.setDirection(orientation)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
        self.pos = pygame.math.Vector2(location)
        self.setTarget(self.pos)
        self.speed = speed
    
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
        if pos[0] > 0 and pos[0] < DISPLAY_WIDTH: #and pos[1] > 0 and pos[1] < DISPLAY_HEIGHT:
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
        
    def update(self):
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

class Building(pygame.sprite.Sprite):
    def __init__(self, img, locX=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
    
    # based on https://stackoverflow.com/questions/60997970/how-to-add-a-text-speech-in-pygame
    def sayHello(self, text : str, color, bold : bool):
        font = FONT_ARIAL
        font.set_bold(bold)
        textSurf = font.render(text, True, color, WHITE).convert_alpha()
        textSize = textSurf.get_size()   
        bubbleSurf = pygame.Surface((textSize[0]*2, textSize[1]*2))
        bubbleRect = bubbleSurf.get_rect()
        pygame.draw.rect(bubbleSurf, color, bubbleRect, 3)
        bubbleSurf.blit(textSurf, textSurf.get_rect(center = bubbleRect.center))
        bubbleRect.center = (self.rect.center[0], self.rect.center[1]-100)
        gameDisplay.blit(bubbleSurf, bubbleRect)



# Initialize pygame
pygame.init()

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Silly Inventions!')

clock = pygame.time.Clock()

# Load everthing
IMG_FACTORY = load_image_file("factory512px.png", (128,128))
IMG_SHOP = load_image_file("shop512px.png", (128,128))
IMG_TRUCK = load_image_file("truck64px.png")
# Icons made by https://www.flaticon.com/authors/nhor-phai

FONT_ARIAL = pygame.font.SysFont('Arial', 18)

# Create world surface?


# Create the player
player1 = Truck(50)
player2 = Truck(DISPLAY_WIDTH - IMG_TRUCK.get_width() - 50, orientation="LEFT")

# Create buildings group for collision detection and position updates
buildings = pygame.sprite.Group()
buildings.add(Building(IMG_FACTORY, 200))
buildings.add(Building(IMG_SHOP, 600))
buildings.add(Building(IMG_FACTORY, DISPLAY_WIDTH - IMG_FACTORY.get_width() - 200,))

# - Create allSprites group for rendering
all_sprites = pygame.sprite.Group()
for b in buildings:
    all_sprites.add(b)
# players on top of buildings
all_sprites.add(player1)
all_sprites.add(player2)

done = False

# Main loop
while not done:
    # Look at every event in the queue
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()

    # check pressed keys
    keys = pygame.key.get_pressed()

    # q or escape to quit
    if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
        pygame.quit()

    # left and right to move player1
    if keys[pygame.K_a]: # left
        player1.move((-1,0))
    elif keys[pygame.K_d]: # right
        player1.move((1,0))

    # left and right to move player2
    if keys[pygame.K_LEFT]:
        player2.move((-1,0))
    elif keys[pygame.K_RIGHT]:
        player2.move((1,0))
    
    # up and down to change speed
    if keys[pygame.K_UP]:
        player1.changeSpeed(1)
        player2.changeSpeed(1)
    elif keys[pygame.K_DOWN]:
        player1.changeSpeed(-1)
        player2.changeSpeed(-1)
    
    # checking pressed mouse and move the player around
    click = pygame.mouse.get_pressed()
    if click[0] == True: # evaluate left button
        player1.setTarget(pygame.mouse.get_pos())
    
    # Updates
    player1.update()
    player2.update()

    # init background
    gameDisplay.fill(WHITE)
    pygame.draw.line(gameDisplay, BLACK, (0, GROUND), (DISPLAY_WIDTH, GROUND), 5)    

    all_sprites.draw(gameDisplay)

    # Check if players have collided with a building
    collided_buildings = pygame.sprite.spritecollide(player1,buildings,False)
    for building in collided_buildings:
        # If so, then factory should say hello
        building.sayHello('Hello!', BLACK, False)
    collided_buildings = pygame.sprite.spritecollide(player2,buildings,False)
    for building in collided_buildings:
        # If so, then factory should say hello
        building.sayHello('Hello!', BLACK, False)

     # Update the display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
