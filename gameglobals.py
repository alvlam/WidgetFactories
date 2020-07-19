
import pygame as pg

pg.init()

# pre-load font
FONT_ARIAL = pg.font.SysFont('Arial', 18)

SINGLE_PLAYER = True # TO DO: make this selectable via menu

P1_MAP = {
        pg.K_a: ("move", (-1, 0)),
        pg.K_d: ("move", (1, 0)),
        pg.K_w: ("speed", 1),
        pg.K_s: ("speed", -1),
        pg.K_e: ("place", 0)}
P2_MAP = {
        pg.K_LEFT: ("move", (-1, 0)),
        pg.K_RIGHT: ("move", (1, 0)),
        pg.K_UP: ("speed", 1),
        pg.K_DOWN: ("speed", -1),
        pg.K_p: ("place", 0)}

# DISPLAY SIZE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Set up world surface, as globals for objects to access
WORLD_WIDTH = 2000
WORLD_HEIGHT = 400
WORLD_SURFACE = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))
GROUND = WORLD_SURFACE.get_height() - 100 # ground height

# Image file names 
# Icons made by https://www.flaticon.com/authors/nhor-phai
TRUCK_FILENAME = "truck64px.png"
FACTORY_FILENAME = "factory512px.png"
SHOP_FILENAME = "shop512px.png"

# Create global sprite groups
BUILDINGS = pg.sprite.Group()
ALL_SPRITES = pg.sprite.LayeredUpdates()
