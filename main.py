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

# load image files
def load_image_file(fileName, resize=None):
    img = pygame.image.load(path.join(path.dirname(__file__), fileName))
    if resize is not None:
        img = pygame.transform.scale(img, resize)
    return img

IMG_FACTORY = load_image_file("img/factory64px.png", (128,128))
IMG_TRUCK = load_image_file("img/truck64px.png")
# Icons made by <a href="https://www.flaticon.com/authors/nhor-phai" title="Nhor Phai">Nhor Phai</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>

def factory(loc):
    gameDisplay.blit(IMG_FACTORY, (loc, GROUND - IMG_FACTORY.get_height()))


#------ Sprite definitions ------------------------------
class Truck(pygame.sprite.Sprite):
    def __init__(self, locX, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMG_TRUCK
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        location = (locX, GROUND - self.image.get_height())
        self.rect.topleft = location
        self.pos = pygame.math.Vector2(location)
        self.set_target(self.pos)
        self.speed = speed
        
        self.autoMoving = False

    def set_target(self, pos):
        if pos[0] > 0 and pos[0] < DISPLAY_WIDTH: #and pos[1] > 0 and pos[1] < DISPLAY_HEIGHT:
            self.target = pygame.math.Vector2((pos[0], self.pos[1]))
        else:
            self.target = self.pos
    
    def move(self, vector):
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
    
    def set_direction(self, direction):
        if direction == "left":
          if self.orientation == "Right":
        self.screen.blit(self.image, self.rect)
    elif self.orientation == "Left":
        self.screen.blit(pygame.transform.flip(self.image, False, True), self.rect)


# Initialize pygame
pygame.init()

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Silly Inventions!')

clock = pygame.time.Clock()

# Create sprites
truck = pygame.sprite.GroupSingle(Truck(50,1))

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
        truck.sprite.move((-1,0))
    elif keys[pygame.K_RIGHT]:
        truck.sprite.move((1,0))
    
    # checking pressed mouse and move the player around
    click = pygame.mouse.get_pressed()
    if click[0] == True: # evaluate left button
        truck.sprite.set_target(pygame.mouse.get_pos())
    
    # Updates
    truck.sprite.update()

    # init background
    gameDisplay.fill(WHITE)
    pygame.draw.line(gameDisplay, BLACK, (0, GROUND), (DISPLAY_WIDTH, GROUND), 5)    
    factory(300)
    truck.draw(gameDisplay)

     # Update the display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
