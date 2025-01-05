import pygame
import config
import sprites
import math
import random

class Game:
    def __init__(self):
        # Initialize Pygame and set up game window
        pygame.init()
        pygame.display.set_caption("BS_simulator")
        self.config = config.Config()
        self.screen = pygame.display.set_mode(self.config.AREA)
        self.clock = pygame.time.Clock()
        self.load_image()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.carsprites=[]
        self.BS_sprites=[]
        # Tracking metrics and mode settings
        self.tme=0
        self.mode=0
        self.switch_count_best_effort=0
        self.switch_count_minimum_threshold=0
        self.switch_count_entropy=0
        self.switch_count_admission_nearby=0
        self.number_of_calling_car=0
        self.BG_and_BS_create_func()
        self.car_create_func()

    def load_image(self):
        # # Assets
        # Load and set up images for background and animations
        self.bg_image = pygame.image.load("../image/BS_2.png").convert()
        self.X_animation = {
            'normal': [pygame.transform.scale(
                pygame.image.load(f"../image/X{i}.png").convert(), (20, 20)
            ) for i in range(1, 4)]
        }
    def draw_text(self,surf, text, size, x, y, color):
        font = pygame.font.Font(self.config.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surf.blit(text_surface, text_rect)

    def draw_line(self,surf, linecolor, start, end, width):
        pygame.draw.line(surf, linecolor, start, end, width)
    def draw_car_text(self,surf, text, size, x, y):
        font = pygame.font.Font(self.config.font_name, size)
        text_surface = font.render(text, True, self.config.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.centery = y
        surf.blit(text_surface, text_rect)
    # Calculate the Euclidean distance between two points
    def calculate_dis(self,car_x, car_y, bs_x, bs_y):
        return math.sqrt((car_x - bs_x) ** 2 + (car_y - bs_y) ** 2)
    # Calculate the dB value based on distance and base station power
    def calculate_DB(self,freq, dis):
        return self.config.PT - (32.45 + 20 * math.log(freq, 10) + 20 * math.log(dis, 10))
    def BG_and_BS_create_func(self):
        for i in range(10):
            for j in range(10): 
                bg = sprites.BG((((self.config.BLOCK_SIZE+10)*i)+10),(((self.config.BLOCK_SIZE+10)*j)+10))
                self.all_sprites.add(bg)
                bsrand = random.randrange(0, 10000)
                if bsrand%10==0:
                    bs = sprites.BS((((self.config.BLOCK_SIZE+10)*i)+10),(((self.config.BLOCK_SIZE+10)*j)+10),self.bg_image)
                    self.all_sprites.add(bs)
                    bs.DBpower=random.randrange(1,11)*100
                    self.BS_sprites.append(bs)
    # Create and assign properties to a car object
    def car_create(self,car):
        self.all_sprites.add(car)
        self.carsprites.append(car)
        # Determine the best base station based on signal strength
        DB_MAX=-1
        strongest_bs=-1
        for j in range(len(self.BS_sprites)):
            dis=self.calculate_dis(car.rect.centerx,car.rect.centery,self.BS_sprites[j].rect.centerx,self.BS_sprites[j].rect.centery)
            DB=self.calculate_DB(self.BS_sprites[j].DBpower,dis*self.config.Distance_scaler)
            if DB>DB_MAX:
                DB_MAX=DB
                strongest_bs=j
            self.BS_sprites[strongest_bs].load_car_best_effort+=1
            self.BS_sprites[strongest_bs].load_car_minimum_threshold+=1
            self.BS_sprites[strongest_bs].load_car_entropy+=1
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
        for j in range(len(self.BS_sprites)):
            dis=self.calculate_dis(car.rect.centerx,car.rect.centery,self.BS_sprites[j].rect.centerx,self.BS_sprites[j].rect.centery)
            DB=self.calculate_DB(self.BS_sprites[j].DBpower,dis*self.config.Distance_scaler)
            if DB>DB_MAX:
                DB_MAX=DB
                strongest_bs=j
            if dis<=self.config.radius/self.config.Distance_scaler:
                if DB>DB_nearby_MAX:
                    DB_nearby_MAX=DB
                    strongest_nearby_bs=j
        if DB_nearby_MAX==-1 or strongest_nearby_bs==-1:
            self.BS_sprites[strongest_bs].load_car_admission_nearby+=1
            car.BS_admission_nearby=strongest_bs
            car.DB_admission_nearby=DB_MAX
        else:
            self.BS_sprites[strongest_nearby_bs].load_car_admission_nearby+=1
            car.BS_admission_nearby=strongest_nearby_bs
            car.DB_admission_nearby=DB_nearby_MAX



    def car_create_func(self):
        for i in range(1,10):
            if random.randrange(0,self.config.prob_amplifier)<=self.config.poisson_prob*self.config.prob_amplifier:
                car=sprites.Car(0,(self.config.BLOCK_SIZE+10)*i,1,(255,0,0),self.explosion_and_new_born)
                self.car_create(car)
            if random.randrange(0,self.config.prob_amplifier)<=self.config.poisson_prob*self.config.prob_amplifier:
                car=sprites.Car((self.config.BLOCK_SIZE+10)*10,(self.config.BLOCK_SIZE+10)*i,3,(0,255,0),self.explosion_and_new_born)
                self.car_create(car)
            if random.randrange(0,self.config.prob_amplifier)<=self.config.poisson_prob*self.config.prob_amplifier:
                car=sprites.Car((self.config.BLOCK_SIZE+10)*i,0,2,(0,255,255),self.explosion_and_new_born)
                self.car_create(car)
            if random.randrange(0,self.config.prob_amplifier)<=self.config.poisson_prob*self.config.prob_amplifier:
                car=sprites.Car((self.config.BLOCK_SIZE+10)*i,(self.config.BLOCK_SIZE+10)*10,0,(255,255,0),self.explosion_and_new_born)
                self.car_create(car)
    def explosion_and_new_born(self,car):
        expl_X = sprites.Explosion_X(car.rect.center, 'normal', 20,self.X_animation)
        self.all_sprites.add(expl_X)
        self.carsprites.remove(car)
        car.kill()
    def handle_events(self):
        for event in pygame.event.get():  
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    elif event.key== pygame.K_0:
                        self.mode=0
                    elif event.key== pygame.K_1:
                        self.mode=1
                    elif event.key== pygame.K_2:
                        self.mode=2
                    elif event.key== pygame.K_3:
                        self.mode=3
                    elif event.key== pygame.K_4:
                        self.mode=4

    def update(self):
        self.tme+=1
        for car in self.carsprites:
            self.update_best_effort(car)
            self.update_minimum_threshold(car)
            self.update_entropy(car)
            self.update_admission_nearby(car)
     # Update car connection using "best effort" strategy
    def update_best_effort(self,car):
        DB_MAX = car.DB_best_effort
        strongest_bs = car.BS_best_effort

        for i, bs in enumerate(self.BS_sprites):
            dis = self.calculate_dis(car.rect.centerx, car.rect.centery, bs.rect.centerx, bs.rect.centery)
            DB = self.calculate_DB(bs.DBpower, dis * self.config.Distance_scaler)
            if DB > DB_MAX:
                DB_MAX = DB
                strongest_bs = i

        car.DB_best_effort = DB_MAX
        if self.mode==0:
            self.draw_line(self.screen,(255,0,0),(car.rect.centerx-5,car.rect.centery-5),(self.BS_sprites[strongest_bs].rect.centerx-15,self.BS_sprites[strongest_bs].rect.centery-15),2)
            self.draw_car_text(self.screen,str(int(car.DB_best_effort))+" dB",15,car.rect.centerx+10,car.rect.centery-27)
        elif self.mode==1:
            self.draw_line(self.screen,(255,0,0),(car.rect.centerx,car.rect.centery),(self.BS_sprites[strongest_bs].rect.centerx,self.BS_sprites[strongest_bs].rect.centery),2)
            self.draw_car_text(self.screen,str(int(car.DB_best_effort))+" dB",15,car.rect.centerx+10,car.rect.centery)

        if strongest_bs != car.BS_best_effort:
            self.switch_count_best_effort += 1
        self.BS_sprites[strongest_bs].load_car_best_effort += 1
        car.BS_best_effort = strongest_bs


    def update_minimum_threshold(self,car):
        DB_now = car.DB_minimum_threshold
        BS_now = car.BS_minimum_threshold

        if car.DB_minimum_threshold < self.config.threshold:
            for i, bs in enumerate(self.BS_sprites):
                dis = self.calculate_dis(car.rect.centerx, car.rect.centery, bs.rect.centerx, bs.rect.centery)
                DB = self.calculate_DB(bs.DBpower, dis * self.config.Distance_scaler)
                if DB > DB_now:
                    DB_now = DB
                    BS_now = i

        car.DB_minimum_threshold = DB_now
        if BS_now != car.BS_minimum_threshold:
            self.switch_count_minimum_threshold += 1
        self.BS_sprites[BS_now].load_car_minimum_threshold += 1
        car.BS_minimum_threshold = BS_now
        if self.mode==0 :
            self.draw_line(self.screen,(0,255,0),(car.rect.centerx+5,car.rect.centery-5),(self.BS_sprites[car.BS_minimum_threshold].rect.centerx+15,self.BS_sprites[car.BS_minimum_threshold].rect.centery-15),2)
            self.draw_car_text(self.screen,str(int(car.DB_minimum_threshold))+" dB",15,car.rect.centerx+10,car.rect.centery-9)
        elif self.mode==2:
            self.draw_line(self.screen,(0,255,0),(car.rect.centerx,car.rect.centery),(self.BS_sprites[car.BS_minimum_threshold].rect.centerx,self.BS_sprites[car.BS_minimum_threshold].rect.centery),2)
            self.draw_car_text(self.screen,str(int(car.DB_minimum_threshold))+" dB",15,car.rect.centerx+10,car.rect.centery)

    def update_entropy(self,car):
        DB_now = car.DB_entropy
        BS_now = car.BS_entropy
        DB_MAX = -1
        strongest_bs = -1

        for i, bs in enumerate(self.BS_sprites):
            dis = self.calculate_dis(car.rect.centerx, car.rect.centery, bs.rect.centerx, bs.rect.centery)
            DB = self.calculate_DB(bs.DBpower, dis * self.config.Distance_scaler)
            if DB > DB_MAX:
                DB_MAX = DB
                strongest_bs = i

        if DB_MAX > DB_now and DB_MAX - DB_now >= self.config.ENTROPY:
            BS_now = strongest_bs
            DB_now = DB_MAX

        car.DB_entropy = DB_now
        if BS_now != car.BS_entropy:
            self.switch_count_entropy += 1
        self.BS_sprites[BS_now].load_car_entropy += 1
        car.BS_entropy = BS_now
        if self.mode==0:
            self.draw_line(self.screen,(0,0,255),(car.rect.centerx-5,car.rect.centery+5),(self.BS_sprites[BS_now].rect.centerx-15,self.BS_sprites[BS_now].rect.centery+15),2)
            self.draw_car_text(self.screen,str(int(car.DB_entropy))+" dB",15,car.rect.centerx+10,car.rect.centery+9)
        elif self.mode==3:
            self.draw_line(self.screen,(0,0,255),(car.rect.centerx,car.rect.centery),(self.BS_sprites[BS_now].rect.centerx,self.BS_sprites[BS_now].rect.centery),2)
            self.draw_car_text(self.screen,str(int(car.DB_entropy))+" dB",15,car.rect.centerx+10,car.rect.centery)


    def update_admission_nearby(self,car):
        DB_nearby_MAX = -1
        strongest_nearby_bs = -1
        DB_MAX = -1
        strongest_bs = -1

        for i, bs in enumerate(self.BS_sprites):
            dis = self.calculate_dis(car.rect.centerx, car.rect.centery, bs.rect.centerx, bs.rect.centery)
            DB = self.calculate_DB(bs.DBpower, dis * self.config.Distance_scaler)
            if DB > DB_MAX:
                DB_MAX = DB
                strongest_bs = i
            if dis <= (self.config.radius / self.config.Distance_scaler):
                if DB > DB_nearby_MAX:
                    DB_nearby_MAX = DB
                    strongest_nearby_bs = i

        if DB_nearby_MAX == -1 or strongest_nearby_bs == -1:
            car.BS_admission_nearby = strongest_bs
            car.DB_admission_nearby = DB_MAX
        else:
            car.BS_admission_nearby = strongest_nearby_bs
            car.DB_admission_nearby = DB_nearby_MAX

        self.switch_count_admission_nearby += 1
        if self.mode==0:
            self.draw_line(self.screen,(255,255,0),(car.rect.centerx+5,car.rect.centery+5),(self.BS_sprites[car.BS_admission_nearby].rect.centerx+15,self.BS_sprites[car.BS_admission_nearby].rect.centery+15),2)
            self.draw_car_text(self.screen,str(int(car.DB_admission_nearby))+" dB",15,car.rect.centerx+10,car.rect.centery+27)
        elif self.mode==4:
            self.draw_line(self.screen,(255,255,0),(car.rect.centerx,car.rect.centery),(self.BS_sprites[car.BS_admission_nearby].rect.centerx,self.BS_sprites[car.BS_admission_nearby].rect.centery),2)
            self.draw_car_text(self.screen,str(int(car.DB_admission_nearby))+" dB",15,car.rect.centerx+10,car.rect.centery)


    def draw_before_BS(self):
       	for i in range(len(self.BS_sprites)):
            self.draw_text(self.screen,str(i+1),15,self.BS_sprites[i].rect.x+self.config.BS_SIZE-((self.config.BS_SIZE)/6),self.BS_sprites[i].rect.y+self.config.BS_SIZE-((self.config.BS_SIZE)/6),self.config.RED)
            self.BS_sprites[i].load_car_best_effort=0
            self.BS_sprites[i].load_car_minimum_threshold=0
            self.BS_sprites[i].load_car_entropy=0
            self.BS_sprites[i].load_car_admission_nearby=0
            self.draw_text(self.screen,"BS "+str(i+1)+"`s bandwidth:"+str(self.BS_sprites[i].DBpower)+" MHz",18,(self.config.BLOCK_SIZE+10)*10+100,80+30*i,self.config.BLACK)
    
    def draw_after_info(self):
        if self.mode==0 or self.mode==1:
            self.draw_text(self.screen,"Best Effort",18,(self.config.BLOCK_SIZE+10)*10+300,20,self.config.BLACK)
            self.draw_text(self.screen,"Switch Times:"+str(self.switch_count_best_effort),18,(self.config.BLOCK_SIZE+10)*10+300,self.config.HEIGHT-50,self.config.BLACK)
        if self.mode==0 or self.mode==2:
            self.draw_text(self.screen,"Minimum threshold",18,(self.config.BLOCK_SIZE+10)*10+450,20,self.config.BLACK)
            self.draw_text(self.screen,"Switch Times:"+str(self.switch_count_minimum_threshold),18,(self.config.BLOCK_SIZE+10)*10+450,self.config.HEIGHT-50,self.config.BLACK)
        if self.mode==0 or self.mode==3:
            self.draw_text(self.screen,"Entropy",18,(self.config.BLOCK_SIZE+10)*10+600,20,self.config.BLACK)
            self.draw_text(self.screen,"Switch Times:"+str(self.switch_count_entropy),18,(self.config.BLOCK_SIZE+10)*10+600,self.config.HEIGHT-50,self.config.BLACK)
        if self.mode==0 or self.mode==4:
            self.draw_text(self.screen,"Admission Nearby",18,(self.config.BLOCK_SIZE+10)*10+750,20,self.config.BLACK)
            self.draw_text(self.screen,"Switch Times:"+str(self.switch_count_admission_nearby),18,(self.config.BLOCK_SIZE+10)*10+750,self.config.HEIGHT-50,self.config.BLACK)

        for i in range(len(self.BS_sprites)):
            if self.mode==0 or self.mode==1:
                self.draw_text(self.screen,"BS "+str(i+1)+" load "+str(self.BS_sprites[i].load_car_best_effort)+ "car(s)",18,(self.config.BLOCK_SIZE+10)*10+300,80+30*i,self.config.BLACK)
            if self.mode==0 or self.mode==2:
                self.draw_text(self.screen,"BS "+str(i+1)+" load "+str(self.BS_sprites[i].load_car_minimum_threshold)+ "car(s)",18,(self.config.BLOCK_SIZE+10)*10+450,80+30*i,self.config.BLACK)
            if self.mode==0 or self.mode==3:
                self.draw_text(self.screen,"BS "+str(i+1)+" load "+str(self.BS_sprites[i].load_car_entropy)+ "car(s)",18,(self.config.BLOCK_SIZE+10)*10+600,80+30*i,self.config.BLACK)
            if self.mode==0 or self.mode==4:
                self.draw_text(self.screen,"BS "+str(i+1)+" load "+str(self.BS_sprites[i].load_car_admission_nearby)+ "car(s)",18,(self.config.BLOCK_SIZE+10)*10+750,80+30*i,self.config.BLACK)



    def draw(self):
        self.screen.fill((255, 192, 203))  # 粉紅背景
        self.all_sprites.draw(self.screen)
        self.draw_before_BS()
        self.draw_text(self.screen,"Time(min):"+str(round(self.tme/60)),18,(self.config.BLOCK_SIZE+10)*10+100,20,self.config.BLACK)
        self.draw_text(self.screen,"Total car:"+str(len(self.carsprites)),18,(self.config.BLOCK_SIZE+10)*10+100,self.config.HEIGHT-50,self.config.BLACK)
        self.draw_text(self.screen,"view mode =>   0:all_mode     1:best_effort     2:minimum_threshold     3:entropy    4:admission_nearby",20,(self.config.BLOCK_SIZE+10)*10+450,self.config.HEIGHT-15,(230,0,255))

    def run(self):
        while self.running:
            self.clock.tick(self.config.FPS)
            self.handle_events()
            self.draw()
            self.car_create_func()
            self.update()
            self.draw_after_info()
            self.all_sprites.update()
            pygame.display.update()
        pygame.quit() 