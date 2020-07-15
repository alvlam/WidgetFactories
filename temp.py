import sys
from random import randint

import pygame as pg

p1_map = {
        pg.K_a: (-1, 0),
        pg.K_d: (1, 0),
        pg.K_w: (0, -1),
        pg.K_s: (0, 1)}
p2_map = {
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (1, 0),
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, 1)}
        
        

class Player(pg.sprite.Sprite):
    def __init__(self, screen_size, center, control_map, cam_origin):
        self.rect = pg.Rect(0, 0, 32, 32)
        self.rect.center = center
        self.screen_rect = self.rect.copy()
        self.cam = pg.Rect(0, 0, screen_size[0], screen_size[1] // 2)
        self.controls = control_map
        self.cam_origin = cam_origin #topleft of screen split rect
        
    def update(self, keys):
        for control in self.controls:
            if keys[control]:
                self.rect.move_ip(self.controls[control])
        self.cam.center = self.rect.center
        self.screen_rect.left = self.rect.left - self.cam.left + self.cam_origin[0]
        self.screen_rect.top = self.rect.top - self.cam.top + self.cam_origin[1]
            
class Game(object):
    def __init__(self, screen_size):
        self.done = False
        self.screen_size = screen_size
        self.screen = pg.display.set_mode(screen_size)
        self.clock = pg.time.Clock()
        self.fps = 60
        self.bg_color = pg.Color("gray5")
        
        self.maze_surface = pg.Surface((3000, 3000))
        self.maze_surface.fill(pg.Color("dodgerblue"))
        for _ in range(50):
            x = randint(0, 3000)
            y = randint(0, 3000)
            color = "gray{}".format(randint(20, 80))
            pg.draw.rect(self.maze_surface, pg.Color(color), (x, y, 20, 20))
        
        self.player1 = Player(screen_size, (screen_size[0] // 2, screen_size[1] // 4 ), p1_map, (0, 0))
        centerx = self.maze_surface.get_width() - (screen_size[0] // 2)
        centery = self.maze_surface.get_height() - (screen_size[1] // 4)
        self.player2 = Player(screen_size, (centerx, centery), p2_map, (0, self.screen_size[1] // 2))
        
        
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                
    def update(self, dt):
        keys = pg.key.get_pressed()
        self.player1.update(keys)
        self.player2.update(keys)
        print "r: {}".format(self.player2.rect)
        print "c: {}".format(self.player2.cam)
        print "s: {}".format(self.player2.screen_rect)
        
    def draw(self):
        self.screen.fill(self.bg_color)
        p1_view = self.maze_surface.subsurface(self.player1.cam)
        self.screen.blit(p1_view, (0, 0))
        pg.draw.rect(self.screen, pg.Color("darkgreen"), self.player1.screen_rect)
        p2_view = self.maze_surface.subsurface(self.player2.cam)
        self.screen.blit(p2_view, (0, self.screen_size[1] // 2))
        pg.draw.rect(self.screen, pg.Color("goldenrod"), self.player2.screen_rect)
        pg.draw.line(self.screen, pg.Color("black"), (0, self.screen_size[1] // 2),
                    (self.screen_size[0], self.screen_size[1] // 2), 2)
        
    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pg.display.update()
            
       
if __name__ == "__main__":
    game = Game((1280, 720))
    game.run()
    pg.quit()
    sys.exit()
