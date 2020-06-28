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
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

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
    def __init__(self, locX=0, speed=1, orientation="RIGHT"):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMG_TRUCK
        self.orientation = orientation
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
        self.pos = pygame.math.Vector2(location)
        self.set_target(self.pos)
        self.speed = speed
    
    def set_direction(self, direction):
        if direction.upper() == "LEFT":
            if self.orientation == "RIGHT":
              self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = "LEFT"
        else:
            if self.orientation == "LEFT":
              self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = "RIGHT"
    
    def set_target(self, pos):
        if pos[0] > 0 and pos[0] < DISPLAY_WIDTH: #and pos[1] > 0 and pos[1] < DISPLAY_HEIGHT:
            # set orientation and flip image if necessary
            if pos[0] < self.pos[0]:
              self.set_direction("LEFT")
            else:
              self.set_direction("RIGHT")
            self.target = pygame.math.Vector2((pos[0], self.pos[1]))
        else:
            self.target = self.pos
    
    def move(self, vector):
      # set orientation and flip image if necessary
      if vector[0] < 0:
        self.set_direction("LEFT")
      else:
        self.set_direction("RIGHT")
      self.set_target((self.rect.left+(vector[0]*self.speed),self.rect.top+(vector[1]*self.speed)))
    
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

class Factory(pygame.sprite.Sprite):
    def __init__(self, locX=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMG_FACTORY
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
IMG_FACTORY = load_image_file("factory64px.png", (128,128))
IMG_TRUCK = load_image_file("truck64px.png")
# Icons made by <a href="https://www.flaticon.com/authors/nhor-phai" title="Nhor Phai">Nhor Phai</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>

FONT_ARIAL = pygame.font.SysFont('Arial', 18)

# Create the player
truck = Truck(50)
factory1 = Factory(200)

# Create groups to hold enemy sprites and all sprites
# - factories is used for collision detection and position updates
# - allSprites is used for rendering
factories = pygame.sprite.Group()
factories.add(factory1)

all_sprites = pygame.sprite.Group()
for f in factories:
    all_sprites.add(f)

# truck on top of factories
all_sprites.add(truck)

done = False

# Main loop
while not done:
    # Look at every event in the queue
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()

    # check pressed keys and move the player around
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        truck.move((-1,0))
    elif keys[pygame.K_RIGHT]:
        truck.move((1,0))
    
    # checking pressed mouse and move the player around
    click = pygame.mouse.get_pressed()
    if click[0] == True: # evaluate left button
        truck.set_target(pygame.mouse.get_pos())
    
    # Updates
    truck.update()

    # init background
    gameDisplay.fill(WHITE)
    pygame.draw.line(gameDisplay, BLACK, (0, GROUND), (DISPLAY_WIDTH, GROUND), 5)    

    all_sprites.draw(gameDisplay)

    # Check if truck has collided with a factory
    collided_factories = pygame.sprite.spritecollide(truck,factories,False)
    for factory in collided_factories:
        # If so, then factory should say hello
        factory.sayHello('Hello!', BLACK, False)

     # Update the display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
