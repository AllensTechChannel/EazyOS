import os
import pygame as pg
import random

LOGO_PATH = 'DVD_logo.png'

class DVD:
    def __init__(self, window) -> None:
        self.window = window
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.window.get_size()
        
        self.sprite = pg.image.load(LOGO_PATH)
        self.scaleDown_ratio = 6
        self.width = self.sprite.get_width() // self.scaleDown_ratio
        self.height = self.sprite.get_height() // self.scaleDown_ratio
        self.logo = pg.transform.scale(self.sprite, (self.width, self.height))
        
        self.gap = 10
        self.screen_offset = 5
        self.x = random.randint(self.gap, self.SCREEN_WIDTH - self.width - self.gap)
        self.y = random.randint(self.gap, self.SCREEN_HEIGHT - self.height - self.gap)
        
        self.velocity = 3
        self.dx = self.velocity if random.randint(0, 1) == 1 else -self.velocity
        self.dy = self.velocity if random.randint(0, 1) == 1 else -self.velocity
        
        self.color = (0, 0, 0)
        self.newColor = self.getRandomRGBColor()

    def getRandomRGBColor(self):
        return (random.randint(60, 255), random.randint(60, 255), random.randint(60, 255))
        
    def changeColor(self):
        # Note: PixelArray.replace might not work as expected, consider alternative approach
        pg.PixelArray(self.logo).replace(self.color, self.newColor)
        self.color = self.newColor
        self.newColor = self.getRandomRGBColor()
        
    def update(self):
        if self.x < -self.screen_offset or self.x > self.SCREEN_WIDTH - self.width + self.screen_offset:
            self.dx = -self.dx
            self.changeColor()

        if self.y < -self.screen_offset or self.y > self.SCREEN_HEIGHT - self.height + self.screen_offset:
            self.dy = -self.dy
            self.changeColor()

        self.x += self.dx
        self.y += self.dy

    def render(self):
        self.window.blit(self.logo, (self.x, self.y))
