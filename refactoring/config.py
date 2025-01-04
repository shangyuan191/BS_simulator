# config.py
import pygame
import math

# Constants
class Config():
    def __init__(self):
        self.FPS = 60
        self.BLOCK_SIZE = 50
        self.WIDTH = self.BLOCK_SIZE*10+10*11
        self.HEIGHT = self.BLOCK_SIZE*10+10*11
        self.AREA = (self.WIDTH + 900, self.HEIGHT)
        
        self.BS_SIZE = 30
        poisson_lambda=1/1440
        self.poisson_prob=float(((math.e)**(-poisson_lambda))*(poisson_lambda))
        self.prob_amplifier=10000
        self.Distance_scaler = 0.05
        self.radius = 6
        self.V = 1
        self.PT = 200
        self.PROB_AMPLIFIER = 10000
        self.ENTROPY = 10
        self.threshold = 100
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.PURPLE = (160, 32, 240)
        self.RED = (255, 0, 0)
        self.font_name = pygame.font.match_font('arial')

