import pygame
import random
import os
import math

pygame.init()
pygame.display.set_caption("BS_simulator(call_release)")
poisson_lambda=1/720
poisson_prob=float(((math.e)**(-poisson_lambda))*(poisson_lambda))
prob_amplifier=10000
Distance_scaler=0.05
radius=6
FPS=60
V=1
Pt=200
BLOCK_SIZE=50
BS_SIZE=30
entropy=10
Threshold=100
WIDTH = BLOCK_SIZE*10+10*11
HEIGHT = BLOCK_SIZE*10+10*11
AREA = (WIDTH+900, HEIGHT)
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
              period = random.gauss(mu = 180, sigma = 60)
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
    self.load_car_best_effort=0
    self.load_car_minimum_threshold=0
    self.load_car_entropy=0
    self.load_car_admission_nearby=0
    
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
    self.DB_best_effort=0
    self.DB_minimum_threshold=0
    self.DB_entropy=0
    self.DB_admission_nearby=0
    self.BS_best_effort=-1
    self.BS_minimum_threshold=-1
    self.BS_entropy=-1
    self.BS_admission_nearby=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.rest_time=0
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
          self.rest_time=(self.call_time_interval[i][0]+self.call_time_interval[i][1])-self.sec
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
    self.DB_best_effort=0
    self.DB_minimum_threshold=0
    self.DB_entropy=0
    self.DB_admission_nearby=0
    self.BS_best_effort=-1
    self.BS_minimum_threshold=-1
    self.BS_entropy=-1
    self.BS_admission_nearby=-1
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.rest_time=0
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
          self.rest_time=(self.call_time_interval[i][0]+self.call_time_interval[i][1])-self.sec
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
    self.DB_best_effort=0
    self.DB_minimum_threshold=0
    self.DB_entropy=0
    self.DB_admission_nearby=0
    self.BS_best_effort=-1
    self.BS_minimum_threshold=-1
    self.BS_entropy=-1
    self.BS_admission_nearby=-1
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.rest_time=0
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
          self.rest_time=(self.call_time_interval[i][0]+self.call_time_interval[i][1])-self.sec
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
    self.DB_best_effort=0
    self.DB_minimum_threshold=0
    self.DB_entropy=0
    self.DB_admission_nearby=0
    self.BS_best_effort=-1
    self.BS_minimum_threshold=-1
    self.BS_entropy=-1
    self.BS_admission_nearby=-1
    self.speedy=-self.v
    self.position_x=float(self.rect.x)
    self.position_y=float(self.rect.y)
    self.sec=0
    self.call_in_one_hour=0
    self.call_time_interval=[]
    self.iscalling=0
    self.rest_time=0
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
          self.rest_time=(self.call_time_interval[i][0]+self.call_time_interval[i][1])-self.sec
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
switch_count_best_effort=0
switch_count_minimum_threshold=0
switch_count_entropy=0
switch_count_admission_nearby=0
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
    BS_sprites[strongest_bs].load_car_best_effort+=1
    BS_sprites[strongest_bs].load_car_minimum_threshold+=1
    BS_sprites[strongest_bs].load_car_entropy+=1
    car.BS_best_effort=strongest_bs
    car.DB_best_effort=DB_MAX
    car.BS_minimum_threshold=strongest_bs
    car.DB_minimum_threshold=DB_MAX
    car.BS_entropy=strongest_bs
    car.DB_entropy=DB_MAX

  DB_nearby_MAX=-1
  strongest_nearby_bs=-1
  DB_MAX=-1
  strongest_bs=-1
  for j in range(len(BS_sprites)):
    dis=calculate_dis(car.rect.centerx,car.rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
    DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
    if DB>DB_MAX:
      DB_MAX=DB
      strongest_bs=j
    if dis<=radius/Distance_scaler:
      if DB>DB_nearby_MAX:
        DB_nearby_MAX=DB
        strongest_nearby_bs=j
  if DB_nearby_MAX==-1 or strongest_nearby_bs==-1:
    BS_sprites[strongest_bs].load_car_admission_nearby+=1
    car.BS_admission_nearby=strongest_bs
    car.DB_admission_nearby=DB_MAX
  else:
    BS_sprites[strongest_nearby_bs].load_car_admission_nearby+=1
    car.BS_admission_nearby=strongest_nearby_bs
    car.DB_admission_nearby=DB_nearby_MAX
  
  

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


tme=0
mode=0
car_create_func()
while running:
  clock.tick(FPS)
  for event in pygame.event.get():  
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key== pygame.K_0:
                mode=0
            elif event.key== pygame.K_1:
                mode=1
            elif event.key== pygame.K_2:
                mode=2
            elif event.key== pygame.K_3:
                mode=3
            elif event.key== pygame.K_4:
                mode=4
  screen.fill((255,192,203))
  all_sprites.draw(screen)
  
  for i in range(len(BS_sprites)):
    draw_text(screen,str(i+1),15,BS_sprites[i].rect.x+BS_SIZE-((BS_SIZE)/6),BS_sprites[i].rect.y+BS_SIZE-((BS_SIZE)/6),RED)
    BS_sprites[i].load_car_best_effort=0
    BS_sprites[i].load_car_minimum_threshold=0
    BS_sprites[i].load_car_entropy=0
    BS_sprites[i].load_car_admission_nearby=0
    draw_text(screen,"BS "+str(i+1)+"`s bandwidth:"+str(BS_sprites[i].DBpower)+" MHz",18,(BLOCK_SIZE+10)*10+100,80+30*i,BLACK)

  car_create_func()
  number_of_calling_car=0
  tme+=1
  draw_text(screen,"Time(min):"+str(round(tme/60)),18,(BLOCK_SIZE+10)*10+100,20,BLACK)
  draw_text(screen,"Total car:"+str(len(carsprites)),18,(BLOCK_SIZE+10)*10+100,50,BLACK)
  draw_text(screen,"view mode =>   0:all_mode     1:best_effort     2:minimum_threshold     3:entropy    4:admission_nearby",20,(BLOCK_SIZE+10)*10+450,HEIGHT-10,(230,0,255))
  for i in range(len(carsprites)):
    if carsprites[i].iscalling==1:
      draw_car_text(screen,"Remaining time:"+str(round((carsprites[i].rest_time)/60))+" min",15,carsprites[i].rect.centerx-80,carsprites[i].rect.centery)
      number_of_calling_car+=1



      DB_MAX=carsprites[i].DB_best_effort
      strongest_bs=carsprites[i].BS_best_effort
      for j in range(len(BS_sprites)):
        dis=calculate_dis(carsprites[i].rect.centerx,carsprites[i].rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
        DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
        if DB>DB_MAX:
          DB_MAX=DB
          strongest_bs=j
        
        
      
      carsprites[i].DB_best_effort=DB_MAX
      if mode==0:
        draw_line(screen,(255,0,0),(carsprites[i].rect.centerx-5,carsprites[i].rect.centery-5),(BS_sprites[strongest_bs].rect.centerx-15,BS_sprites[strongest_bs].rect.centery-15),2)
        draw_car_text(screen,str(int(carsprites[i].DB_best_effort))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery-27)
      elif mode==1:
        draw_line(screen,(255,0,0),(carsprites[i].rect.centerx,carsprites[i].rect.centery),(BS_sprites[strongest_bs].rect.centerx,BS_sprites[strongest_bs].rect.centery),2)
        draw_car_text(screen,str(int(carsprites[i].DB_best_effort))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery)
      
      if strongest_bs!=carsprites[i].BS_best_effort:
        switch_count_best_effort+=1
      BS_sprites[strongest_bs].load_car_best_effort+=1
      carsprites[i].BS_best_effort=strongest_bs


      DB_now=carsprites[i].DB_minimum_threshold
      BS_now=carsprites[i].BS_minimum_threshold
      if carsprites[i].DB_minimum_threshold<Threshold:
        for j in range(len(BS_sprites)):
          dis=calculate_dis(carsprites[i].rect.centerx,carsprites[i].rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
          DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
          if DB>DB_now:
            DB_now=DB
            BS_now=j
            
      BS_sprites[BS_now].load_car_minimum_threshold+=1
      carsprites[i].DB_minimum_threshold=DB_now
        
      if BS_now!=carsprites[i].BS_minimum_threshold:
        switch_count_minimum_threshold+=1
        carsprites[i].BS_minimum_threshold=BS_now
      if mode==0 :
        draw_line(screen,(0,255,0),(carsprites[i].rect.centerx+5,carsprites[i].rect.centery-5),(BS_sprites[carsprites[i].BS_minimum_threshold].rect.centerx+15,BS_sprites[carsprites[i].BS_minimum_threshold].rect.centery-15),2)
        draw_car_text(screen,str(int(carsprites[i].DB_minimum_threshold))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery-9)
      elif mode==2:
        draw_line(screen,(0,255,0),(carsprites[i].rect.centerx,carsprites[i].rect.centery),(BS_sprites[carsprites[i].BS_minimum_threshold].rect.centerx,BS_sprites[carsprites[i].BS_minimum_threshold].rect.centery),2)
        draw_car_text(screen,str(int(carsprites[i].DB_minimum_threshold))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery)



      DB_now=carsprites[i].DB_entropy
      BS_now=carsprites[i].BS_entropy
      DB_MAX=-1
      strongest_bs=-1
      for j in range(len(BS_sprites)):
        dis=calculate_dis(carsprites[i].rect.centerx,carsprites[i].rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
        DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
        if DB>DB_MAX:
          DB_MAX=DB
          strongest_bs=j
      if DB_MAX>DB_now and DB_MAX-DB_now>=entropy:
        BS_now=strongest_bs
        DB_now=DB_MAX
      carsprites[i].DB_entropy=DB_now
      BS_sprites[BS_now].load_car_entropy+=1
        
      if BS_now!=carsprites[i].BS_entropy:
        switch_count_entropy+=1
        carsprites[i].BS_entropy=BS_now
      if mode==0:
        draw_line(screen,(0,0,255),(carsprites[i].rect.centerx-5,carsprites[i].rect.centery+5),(BS_sprites[BS_now].rect.centerx-15,BS_sprites[BS_now].rect.centery+15),2)
        draw_car_text(screen,str(int(carsprites[i].DB_entropy))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery+9)
      elif mode==3:
        draw_line(screen,(0,0,255),(carsprites[i].rect.centerx,carsprites[i].rect.centery),(BS_sprites[BS_now].rect.centerx,BS_sprites[BS_now].rect.centery),2)
        draw_car_text(screen,str(int(carsprites[i].DB_entropy))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery)





      DB_nearby_MAX=-1
      strongest_nearby_bs=-1
      DB_MAX=-1
      strongest_bs=-1
      for j in range(len(BS_sprites)):
        dis=calculate_dis(carsprites[i].rect.centerx,carsprites[i].rect.centery,BS_sprites[j].rect.centerx,BS_sprites[j].rect.centery)
        DB=calculate_DB(BS_sprites[j].DBpower,dis*Distance_scaler)
        if DB>DB_MAX:
          DB_MAX=DB
          strongest_bs=j
        if dis<=(radius/Distance_scaler):
          if DB>DB_nearby_MAX:
            DB_nearby_MAX=DB
            strongest_nearby_bs=j
      if DB_nearby_MAX==-1 or strongest_nearby_bs==-1:
        if strongest_bs!=carsprites[i].BS_admission_nearby:
          switch_count_admission_nearby+=1
        BS_sprites[strongest_bs].load_car_admission_nearby+=1
        carsprites[i].BS_admission_nearby=strongest_bs
        carsprites[i].DB_admission_nearby=DB_MAX
      else:
        if strongest_nearby_bs!=carsprites[i].BS_admission_nearby:
          switch_count_admission_nearby+=1
        BS_sprites[strongest_nearby_bs].load_car_admission_nearby+=1
        carsprites[i].BS_admission_nearby=strongest_nearby_bs
        carsprites[i].DB_admission_nearby=DB_nearby_MAX
      
      if mode==0:
        draw_line(screen,(255,255,0),(carsprites[i].rect.centerx+5,carsprites[i].rect.centery+5),(BS_sprites[carsprites[i].BS_admission_nearby].rect.centerx+15,BS_sprites[carsprites[i].BS_admission_nearby].rect.centery+15),2)
        draw_car_text(screen,str(int(carsprites[i].DB_admission_nearby))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery+27)
      elif mode==4:
        draw_line(screen,(255,255,0),(carsprites[i].rect.centerx,carsprites[i].rect.centery),(BS_sprites[carsprites[i].BS_admission_nearby].rect.centerx,BS_sprites[carsprites[i].BS_admission_nearby].rect.centery),2)
        draw_car_text(screen,str(int(carsprites[i].DB_admission_nearby))+" dB",15,carsprites[i].rect.centerx+10,carsprites[i].rect.centery)

  if mode==0 or mode==1:
    draw_text(screen,"Best Effort",18,(BLOCK_SIZE+10)*10+300,20,BLACK)
    draw_text(screen,"Switch Times:"+str(switch_count_best_effort),18,(BLOCK_SIZE+10)*10+300,HEIGHT-50,BLACK)
  if mode==0 or mode==2:
    draw_text(screen,"Minimum THreshold",18,(BLOCK_SIZE+10)*10+450,20,BLACK)
    draw_text(screen,"Switch Times:"+str(switch_count_minimum_threshold),18,(BLOCK_SIZE+10)*10+450,HEIGHT-50,BLACK)
  if mode==0 or mode==3:
    draw_text(screen,"Entropy",18,(BLOCK_SIZE+10)*10+600,20,BLACK)
    draw_text(screen,"Switch Times:"+str(switch_count_entropy),18,(BLOCK_SIZE+10)*10+600,HEIGHT-50,BLACK)
  if mode==0 or mode==4:
    draw_text(screen,"Admission Nearby",18,(BLOCK_SIZE+10)*10+750,20,BLACK)
    draw_text(screen,"Switch Times:"+str(switch_count_admission_nearby),18,(BLOCK_SIZE+10)*10+750,HEIGHT-50,BLACK) 
    
  
  
  
  
  for i in range(len(BS_sprites)):
    if mode==0 or mode==1:
      draw_text(screen,"BS "+str(i+1)+" load "+str(BS_sprites[i].load_car_best_effort)+ "car(s)",18,(BLOCK_SIZE+10)*10+300,80+30*i,BLACK)
    if mode==0 or mode==2:
      draw_text(screen,"BS "+str(i+1)+" load "+str(BS_sprites[i].load_car_minimum_threshold)+ "car(s)",18,(BLOCK_SIZE+10)*10+450,80+30*i,BLACK)
    if mode==0 or mode==3:
      draw_text(screen,"BS "+str(i+1)+" load "+str(BS_sprites[i].load_car_entropy)+ "car(s)",18,(BLOCK_SIZE+10)*10+600,80+30*i,BLACK)
    if mode==0 or mode==4:
      draw_text(screen,"BS "+str(i+1)+" load "+str(BS_sprites[i].load_car_admission_nearby)+ "car(s)",18,(BLOCK_SIZE+10)*10+750,80+30*i,BLACK)
  draw_text(screen,"There are "+str(number_of_calling_car)+" car(s) is calling.",18,(BLOCK_SIZE+10)*10+100,HEIGHT-25,BLACK)


  all_sprites.update()
  pygame.display.update()
  
pygame.quit() 


