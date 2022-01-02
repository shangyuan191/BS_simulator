import pygame
import random
import os
import math


pygame.init()
pygame.display.set_caption("BS_simulator <Minimum(Threshold)_call_release>")
poisson_lambda=1/720
poisson_prob=float(((math.e)**(-poisson_lambda))*(poisson_lambda))
prob_amplifier=10000
Distance_scaler=0.05
FPS=60
V=1
Pt=200
Threshold=100
BLOCK_SIZE=50
BS_SIZE=30
WIDTH = BLOCK_SIZE*10+10*11
HEIGHT = BLOCK_SIZE*10+10*11
AREA = (WIDTH+350, HEIGHT)
screen = pygame.display.set_mode(AREA)
clock=pygame.time.Clock()
running=True
bg_image = pygame.image.load(os.path.join("image", "BS_2.png")).convert()
car_image= pygame.image.load(os.path.join("image", "car.png")).convert()
BLACK=(0,0,0)
WHITE=(255,255,255)
PURPLE=(160,32,240)
expl_animation = {}
expl_animation['large'] = []
expl_animation['medium'] = []
expl_animation['small'] = []
expl_animation['player'] = []
expl_animation['super'] = []
for i in range(9):
    expl_image = pygame.image.load(
        os.path.join("image", f"expl{i}.png")).convert()
    expl_image.set_colorkey(BLACK)
    expl_animation['large'].append(
        pygame.transform.scale(expl_image, (75, 75)))
    expl_animation['medium'].append(
        pygame.transform.scale(expl_image, (40, 40)))
    expl_animation['small'].append(
        pygame.transform.scale(expl_image, (15, 15)))
    expl_animation['super'].append(
        pygame.transform.scale(expl_image, (200, 200)))
X_animation={}
X_animation['normal']=[]
for i in range(1,4):
  X_image = pygame.image.load(
        os.path.join("image", f"X{i}.png")).convert()
  X_image.set_colorkey(BLACK)
  X_animation['normal'].append(
        pygame.transform.scale(X_image, (20, 20)))
font_name = pygame.font.match_font('arial')
RED=(255,0,0)
def draw_text(surf, text, size, x, y,color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface, text_rect)
def draw_car_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface, text_rect)
    
def draw_line(surf,linecolor,start,end,width):
  pygame.draw.line(surf,linecolor,start,end,width)

def calculate_dis(car_x,car_y,bs_x,bs_y):
  return ((car_x-bs_x)**2+(car_y-bs_y)**2)**(1/2)

def calculate_DB(freq,dis):
  return Pt-(32.45+20*math.log(freq,10)+20*math.log(dis,10))

def overlap(time1,time2):
    if time1[0] <= time2[1] and time1[1] >= time2[0]:
        return True
    else:
        return False



def set_call_time():
  time_future = []
  is_ok = 0
  call_in_one_hour=round(random.gauss(mu=2.0,sigma=float(2/3)))
  for i in range(call_in_one_hour):
      is_ok = 0
      if i == 0:
          period = random.gauss(mu = 120, sigma = 40)
          period = round(period)
          start_time = random.randrange(0,3600)
          end_time = start_time + period
          if end_time >= 3600:
              i-=1  
          time = (start_time, end_time)
          time_future.append(time)
      else:
          while is_ok == 0:
              count = 0
              period = random.gauss(mu = 120, sigma = 40)
              period = round(period)
              start_time = random.randrange(0,3600)
              end_time = start_time + period
              if end_time >= 3600:
                  continue
              new_time = (start_time,end_time)
              for element in time_future:
                  if overlap(element,new_time) == False:
                      count += 1
              if(count == len(time_future)):
                  time_future.append(new_time)
                  break                
      time_future.sort(key = lambda x: x[0])
  return call_in_one_hour,time_future

class Explosion_X(pygame.sprite.Sprite):
    def __init__(self, center, size, rate):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = X_animation[self.size][0]

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
            if self.frame == len(X_animation[self.size]):
                self.kill()
            else:
                self.image = X_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
class BG(pygame.sprite.Sprite):
  def __init__(self,x,y):
      
    pygame.sprite.Sprite.__init__(self)
    #self.image = pygame.transform.scale(bg_image, (50, 50))
    self.image=pygame.Surface((BLOCK_SIZE,BLOCK_SIZE))
    self.image.fill((34,139,34))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
class BS(pygame.sprite.Sprite):
  def __init__(self,x,y):
    
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.transform.scale(bg_image, (BS_SIZE, BS_SIZE))
    self.rect = self.image.get_rect()
    self.rect.x=x+((BLOCK_SIZE-BS_SIZE)/2)
    self.rect.y=y+((BLOCK_SIZE-BS_SIZE)/2)
    self.DBpower=0
    self.load_car=0
    
    bias=random.randrange(0,4)
    if bias==0:
      self.rect.y-=(BLOCK_SIZE/25)
    elif bias==1:
      self.rect.y+=(BLOCK_SIZE/25)
    elif bias==2:
      self.rect.x-=(BLOCK_SIZE/25)
    elif bias==3:
      self.rect.x+=(BLOCK_SIZE/25)

class CAR_L_to_R(pygame.sprite.Sprite):
  def __init__(self,x,y):
    pygame.sprite.Sprite.__init__(self)
    self.image=pygame.Surface((10,10))
    self.image.fill((255,0,0))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.v=V
    self.speedx=self.v
    self.speedy=0
    self.direct=1
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
    self.DB=0
    self.BS=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
  def explosion_and_new_born(self):
    expl_X = Explosion_X(self.rect.center, 'normal', 20)
    all_sprites.add(expl_X)
    carsprites.remove(self)
    self.kill()
  def update(self):
      self.iscalling=0
      if(self.sec==0):
        self.call_in_one_hour,self.call_time_interval=set_call_time()
      for i in range(len(self.call_time_interval)):
        if(self.sec>=self.call_time_interval[i][0] and self.sec<=self.call_time_interval[i][0]+self.call_time_interval[i][1]):
          self.iscalling=1
      self.position_x+=self.speedx
      self.position_y+=self.speedy
      self.rect.x = round(self.position_x)
      self.rect.y = round(self.position_y)
      if self.rect.x >= WIDTH-10 or self.rect.x<0:
            self.explosion_and_new_born()
            
      if self.rect.y >= HEIGHT-10 or self.rect.y<=0:
            self.explosion_and_new_born()
            
      if self.rect.x%(BLOCK_SIZE+10)==0 and self.rect.y%(BLOCK_SIZE+10)==0 and self.rect.x!=0 and self.rect.x!=(BLOCK_SIZE*10) and self.rect.y!=0 and self.rect.y!=(BLOCK_SIZE*10):
        #0:still the same  1~7:turn right  8~14:turn back  15~31:turn left
        next_direct=random.randrange(0,32)
        if next_direct==0:
          self.direct+=2
        elif next_direct>=1 and next_direct<=7:
          self.direct+=1
        elif next_direct>=8 and next_direct<=14:
          self.direct+=3
        elif next_direct>=15 and next_direct<=31:
          self.direct+=0
        self.direct%=4
        if self.direct==0:
          self.speedy=-self.v
          self.speedx=0
        elif self.direct==1:
          self.speedx=self.v
          self.speedy=0
        elif self.direct==2:
          self.speedx=0
          self.speedy=self.v
        elif self.direct==3:
          self.speedx=-self.v
          self.speedy=0
      self.sec+=1
      if self.sec>=3600:
        self.sec=0    
class CAR_R_to_L(pygame.sprite.Sprite):
  def __init__(self,x,y):
    pygame.sprite.Sprite.__init__(self)
    self.image=pygame.Surface((10,10))
    self.image.fill((0,255,0))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.v=V
    self.speedx=-self.v
    self.speedy=0
    self.direct=3
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
    self.DB=0
    self.BS=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
  def explosion_and_new_born(self):
    expl_X = Explosion_X(self.rect.center, 'normal', 20)
    all_sprites.add(expl_X)
    carsprites.remove(self)
    self.kill()

    
  def update(self):
      self.iscalling=0
      if(self.sec==0):
        self.call_in_one_hour,self.call_time_interval=set_call_time()
      for i in range(len(self.call_time_interval)):
        if(self.sec>=self.call_time_interval[i][0] and self.sec<=self.call_time_interval[i][0]+self.call_time_interval[i][1]):
          self.iscalling=1
      self.position_x+=self.speedx
      self.position_y+=self.speedy
      self.rect.x = round(self.position_x)
      self.rect.y = round(self.position_y)
      if self.rect.x >= WIDTH-10 or self.rect.x<=0:
            self.explosion_and_new_born()
            
      if self.rect.y >= HEIGHT-10 or self.rect.y<=0:

            self.explosion_and_new_born()
      if self.rect.x%(BLOCK_SIZE+10)==0 and self.rect.y%(BLOCK_SIZE+10)==0 and self.rect.x!=0 and self.rect.x!=(BLOCK_SIZE*10) and self.rect.y!=0 and self.rect.y!=(BLOCK_SIZE*10):
        #0:still the same  1~7:turn right  8~14:turn back  15~31:turn left
        next_direct=random.randrange(0,32)
        if next_direct==0:
          self.direct+=2
        elif next_direct>=1 and next_direct<=7:
          self.direct+=1
        elif next_direct>=8 and next_direct<=14:
          self.direct+=3
        elif next_direct>=15 and next_direct<=31:
          self.direct+=0
        self.direct%=4
        if self.direct==0:
          self.speedy=-self.v
          self.speedx=0
        elif self.direct==1:
          self.speedx=self.v
          self.speedy=0
        elif self.direct==2:
          self.speedx=0
          self.speedy=self.v
        elif self.direct==3:
          self.speedx=-self.v
          self.speedy=0
      self.sec+=1
      if self.sec>=3600:
        self.sec=0
class CAR_U_to_D(pygame.sprite.Sprite):
  def __init__(self,x,y):
    pygame.sprite.Sprite.__init__(self)
    self.image=pygame.Surface((10,10))
    self.image.fill((0,255,255))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.v=V
    self.direct=2
    self.speedx=0
    self.speedy=self.v
    self.DB=0
    self.BS=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
  def explosion_and_new_born(self):
    expl_X = Explosion_X(self.rect.center, 'normal', 20)
    all_sprites.add(expl_X)
    carsprites.remove(self)
    self.kill()

  def update(self):
      self.iscalling=0
      if(self.sec==0):
        self.call_in_one_hour,self.call_time_interval=set_call_time()
      for i in range(len(self.call_time_interval)):
        if(self.sec>=self.call_time_interval[i][0] and self.sec<=self.call_time_interval[i][0]+self.call_time_interval[i][1]):
          self.iscalling=1
      self.position_x+=self.speedx
      self.position_y+=self.speedy
      self.rect.x = round(self.position_x)
      self.rect.y = round(self.position_y)
      if self.rect.x >= WIDTH-10 or self.rect.x<=0:
            self.explosion_and_new_born()
      if self.rect.y >= HEIGHT-10 or self.rect.y<0:
            self.explosion_and_new_born()
      if self.rect.x%(BLOCK_SIZE+10)==0 and self.rect.y%(BLOCK_SIZE+10)==0 and self.rect.x!=0 and self.rect.x!=(BLOCK_SIZE*10) and self.rect.y!=0 and self.rect.y!=(BLOCK_SIZE*10):
        #0:still the same  1~7:turn right  8~14:turn back  15~31:turn left
        next_direct=random.randrange(0,32)
        if next_direct==0:
          self.direct+=2
        elif next_direct>=1 and next_direct<=7:
          self.direct+=1
        elif next_direct>=8 and next_direct<=14:
          self.direct+=3
        elif next_direct>=15 and next_direct<=31:
          self.direct+=0
        self.direct%=4
        if self.direct==0:
          self.speedy=-self.v
          self.speedx=0
        elif self.direct==1:
          self.speedx=self.v
          self.speedy=0
        elif self.direct==2:
          self.speedx=0
          self.speedy=self.v
        elif self.direct==3:
          self.speedx=-self.v
          self.speedy=0        
      self.sec+=1
      if self.sec>=3600:
        self.sec=0      
class CAR_D_to_U(pygame.sprite.Sprite):
  def __init__(self,x,y):
    pygame.sprite.Sprite.__init__(self)
    self.image=pygame.Surface((10,10))
    self.image.fill((255,255,0))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.v=V
    self.direct=0
    self.speedx=0
    self.DB=0
    self.BS=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.speedy=-self.v
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
  def explosion_and_new_born(self):
    expl_X = Explosion_X(self.rect.center, 'normal', 20)
    all_sprites.add(expl_X)
    carsprites.remove(self)
    self.kill()  
    
  def update(self):
      self.iscalling=0
      if(self.sec==0):
        self.call_in_one_hour,self.call_time_interval=set_call_time()
      for i in range(len(self.call_time_interval)):
        if(self.sec>=self.call_time_interval[i][0] and self.sec<=self.call_time_interval[i][0]+self.call_time_interval[i][1]):
          self.iscalling=1
      self.position_x+=self.speedx
      self.position_y+=self.speedy
      self.rect.x = round(self.position_x)
      self.rect.y = round(self.position_y)
      if self.rect.x >= WIDTH-10 or self.rect.x<=0:
            self.explosion_and_new_born()
      if self.rect.y >= HEIGHT-10 or self.rect.y<=0:
            self.explosion_and_new_born()
      if self.rect.x%(BLOCK_SIZE+10)==0 and self.rect.y%(BLOCK_SIZE+10)==0 and self.rect.x!=0 and self.rect.x!=(BLOCK_SIZE*10) and self.rect.y!=0 and self.rect.y!=(BLOCK_SIZE*10):
        #0:still the same  1~7:turn right  8~14:turn back  15~31:turn left
        next_direct=random.randrange(0,32)
        if next_direct==0:
          self.direct+=2
        elif next_direct>=1 and next_direct<=7:
          self.direct+=1
        elif next_direct>=8 and next_direct<=14:
          self.direct+=3
        elif next_direct>=15 and next_direct<=31:
          self.direct+=0
        self.direct%=4
        if self.direct==0:
          self.speedy=-self.v
          self.speedx=0
        elif self.direct==1:
          self.speedx=self.v
          self.speedy=0
        elif self.direct==2:
          self.speedx=0
          self.speedy=self.v
        elif self.direct==3:
          self.speedx=-self.v
          self.speedy=0
      self.sec+=1
      if self.sec>=3600:
        self.sec=0          
carsprites=[]
BS_sprites=[]
switch_count=0
all_sprites = pygame.sprite.Group()      
for i in range(10):
  for j in range(10): 
    bg = BG((((BLOCK_SIZE+10)*i)+10),(((BLOCK_SIZE+10)*j)+10))
    all_sprites.add(bg)
    bsrand = random.randrange(0, 10000)
    if bsrand%10==0:
      bs = BS((((BLOCK_SIZE+10)*i)+10),(((BLOCK_SIZE+10)*j)+10))
      all_sprites.add(bs)
      bs.DBpower=random.randrange(1,11)*100
      bs.load_car=0
      BS_sprites.append(bs)

def car_create(car):
  all_sprites.add(car)
  carsprites.append(car)
  DB_MAX=-1
  strongest_bs=-1
  for j in range(len(BS_sprites)):
    dis=calculate_dis(car.rect.centerx,car.rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
    DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
    if DB>DB_MAX:
      DB_MAX=DB
      strongest_bs=j
    BS_sprites[strongest_bs].load_car+=1
    car.BS=strongest_bs
    car.DB=DB_MAX
  

def car_create_func():
  for i in range(1,10):
    if random.randrange(0,prob_amplifier)<=poisson_prob*prob_amplifier:
      car_LR=CAR_L_to_R(0,(BLOCK_SIZE+10)*i)
      car_create(car_LR)
    if random.randrange(0,prob_amplifier)<=poisson_prob*prob_amplifier:
      car_RL=CAR_R_to_L((BLOCK_SIZE+10)*10,(BLOCK_SIZE+10)*i)
      car_create(car_RL)
    if random.randrange(0,prob_amplifier)<=poisson_prob*prob_amplifier:
      car_UD=CAR_U_to_D((BLOCK_SIZE+10)*i,0)
      car_create(car_UD)
    if random.randrange(0,prob_amplifier)<=poisson_prob*prob_amplifier:
      car_DU=CAR_D_to_U((BLOCK_SIZE+10)*i,(BLOCK_SIZE+10)*10)
      car_create(car_DU)



car_create_func()


while running:
  clock.tick(FPS)
  for event in pygame.event.get():  
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
  screen.fill((255,192,203))
  all_sprites.draw(screen)
  
  for i in range(len(BS_sprites)):
    draw_text(screen,str(i+1),15,BS_sprites[i].rect.x+BS_SIZE-((BS_SIZE)/6),BS_sprites[i].rect.y+BS_SIZE-((BS_SIZE)/6),RED)
    BS_sprites[i].load_car=0
  car_create_func()
  number_of_calling_car=0  
  for i in range(len(carsprites)):
    if carsprites[i].iscalling==1:
      number_of_calling_car+=1
      DB_now=carsprites[i].DB
      BS_now=carsprites[i].BS
      if carsprites[i].DB<Threshold:
        for j in range(len(BS_sprites)):
          dis=calculate_dis(carsprites[i].rect.centerx,carsprites[i].rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
          DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
          if DB>DB_now:
            DB_now=DB
            BS_now=j
            
      BS_sprites[BS_now].load_car+=1
      carsprites[i].DB=DB_now
        
      if BS_now!=carsprites[i].BS:
        switch_count+=1
        carsprites[i].BS=BS_now
      draw_line(screen,(0,0,0),(carsprites[i].rect.centerx,carsprites[i].rect.centery),(BS_sprites[carsprites[i].BS].rect.centerx,BS_sprites[carsprites[i].BS].rect.centery),2)
      draw_car_text(screen,str(int(carsprites[i].DB))+" dB",15,carsprites[i].rect.centerx-20,carsprites[i].rect.centery)
  draw_text(screen,"There are "+str(number_of_calling_car)+" car(s) is calling.",30,(BLOCK_SIZE+10)*10+170,HEIGHT-25,BLACK)
  draw_text(screen,"Time(min):"+str(round((pygame.time.get_ticks())/1000)),30,(BLOCK_SIZE+10)*10+170,20,BLACK)
  draw_text(screen,"Switch Times:"+str(switch_count),30,(BLOCK_SIZE+10)*10+170,50,BLACK)
  for i in range(len(BS_sprites)):
    draw_text(screen,"BS "+str(i+1)+"`s bandwidth:"+str(BS_sprites[i].DBpower)+" MHz",18,(BLOCK_SIZE+10)*10+100,80+30*i,BLACK)
    draw_text(screen,"BS "+str(i+1)+" load "+str(BS_sprites[i].load_car)+ "car(s)",18,(BLOCK_SIZE+10)*10+270,80+30*i,BLACK)
  draw_text(screen,"Total car:"+str(len(carsprites)),30,(BLOCK_SIZE+10)*10+170,HEIGHT-65,BLACK)
  all_sprites.update()
  pygame.display.update()
  
pygame.quit() 