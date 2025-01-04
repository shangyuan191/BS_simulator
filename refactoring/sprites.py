import pygame
import config
import random

config= config.Config()
class Explosion_X(pygame.sprite.Sprite):
    def __init__(self, center, size, rate,img):
        pygame.sprite.Sprite.__init__(self)
        self.X_animation = img
        self.size = size
        self.image = self.X_animation[self.size][0]

        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = rate

    def update(self):
        now = pygame.time.get_ticks()
        if now-self.last_update >= self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.X_animation[self.size]):
                self.kill()
            else:
                self.image = self.X_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
class BG(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.transform.scale(bg_image, (50, 50))
		self.image=pygame.Surface((config.BLOCK_SIZE,config.BLOCK_SIZE))
		self.image.fill((34,139,34))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
class BS(pygame.sprite.Sprite):
	def __init__(self,x,y,img):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(img, (config.BS_SIZE, config.BS_SIZE))
		self.rect = self.image.get_rect()
		self.rect.x=x+((config.BLOCK_SIZE-config.BS_SIZE)/2)
		self.rect.y=y+((config.BLOCK_SIZE-config.BS_SIZE)/2)
		self.DBpower=0
		self.load_car_best_effort=0
		self.load_car_minimum_threshold=0
		self.load_car_entropy=0
		self.load_car_admission_nearby=0

		bias=random.randrange(0,4)
		if bias==0:
			self.rect.y-=(config.BLOCK_SIZE/25)
		elif bias==1:
			self.rect.y+=(config.BLOCK_SIZE/25)
		elif bias==2:
			self.rect.x-=(config.BLOCK_SIZE/25)
		elif bias==3:
			self.rect.x+=(config.BLOCK_SIZE/25)
class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color, explosion_callback):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.v = config.V
        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)
        self.explosion_callback = explosion_callback

        # Set direction and speed based on the direction
        self.direction = direction
        if self.direction == 0:  # Down to Up
            self.speedx = 0
            self.speedy = -self.v
        elif self.direction == 1:  # Left to Right
            self.speedx = self.v
            self.speedy = 0
        elif self.direction == 2:  # Up to Down
            self.speedx = 0
            self.speedy = self.v
        elif self.direction == 3:  # Right to Left
            self.speedx = -self.v
            self.speedy = 0

        self.DB_best_effort = 0
        self.DB_minimum_threshold = 0
        self.DB_entropy = 0
        self.DB_admission_nearby = 0
        self.BS_best_effort = -1
        self.BS_minimum_threshold = -1
        self.BS_entropy = -1
        self.BS_admission_nearby = -1



    def update(self):
        self.position_x += self.speedx
        self.position_y += self.speedy
        self.rect.x = round(self.position_x)
        self.rect.y = round(self.position_y)

        if self.rect.x >= config.WIDTH - 10 or self.rect.x <= 0 or self.rect.y >= config.HEIGHT - 10 or self.rect.y <= 0:
            self.explosion_callback(self)

        if self.rect.x % (config.BLOCK_SIZE + 10) == 0 and self.rect.y % (config.BLOCK_SIZE + 10) == 0 and self.rect.x != 0 and self.rect.x != (config.BLOCK_SIZE * 10) and self.rect.y != 0 and self.rect.y != (config.BLOCK_SIZE * 10):
            next_direct = random.randrange(0, 32)
			#0~15:still the same  16~22:turn left  23~29:turn right  30~31:turn back         
            if next_direct >= 0 and next_direct <= 15:
                self.direction += 0
            elif next_direct >= 16 and next_direct <= 22:
                self.direction += 3
            elif next_direct >= 23 and next_direct <= 29:
                self.direction += 1
            elif next_direct >= 30 and next_direct <= 31:
                self.direction += 2
            self.direction %= 4

            # Update speed based on the new direction
            if self.direction == 0:  # Up to Down
                self.speedy = self.v
                self.speedx = 0
            elif self.direction == 1:  # Left to Right
                self.speedx = self.v
                self.speedy = 0
            elif self.direction == 2:  # Down to Up
                self.speedx = 0
                self.speedy = -self.v
            elif self.direction == 3:  # Right to Left
                self.speedx = -self.v
                self.speedy = 0

