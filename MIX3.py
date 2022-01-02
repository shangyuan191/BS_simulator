import pygame
import random 
import math

RUNNING = True
FPS_FRAME = 60
ROAD_SIZE = 15
BLOCK_SIZE = (60,60)
KM_RATIO = (ROAD_SIZE+BLOCK_SIZE[0]) / 2.5
BS_SIZE = (BLOCK_SIZE[0]-35 , BLOCK_SIZE[1]-35 )
MAP_SIZE = ((BLOCK_SIZE[0] + ROAD_SIZE)*10 - ROAD_SIZE , (BLOCK_SIZE[1] + ROAD_SIZE)*10 - ROAD_SIZE)
WINDOW_SIZE = (MAP_SIZE[0] + 500 , MAP_SIZE[1])


Entropy_THRESHOLD = 10.0
Minium_Pmin = 15
MyAlgorithm_error_THRESHOLD = 10.0



vision_db = True
vision_link = True
vision_car = True
filter_idle_car = False
Algorithm_mode = 1
KM_SPEED = 0.02
SPEED = KM_SPEED * KM_RATIO

LAMBDA = float(1/12)

WHITE = (255,255,255)
c_blak = (0, 0, 0)
DAK_YELLOW =(218,165,32)
DAK_RED = (205,50,50)
FIS_RED = (244,141,141)
SPRINT_GREEN = (0,200,114)
FOREST = (34,139,34)
OCEAN = (30,191,255)
DAK_BLUE = (0,128,128)
DAK2_BLUE = (70,130,180)
VIOLET = (138,43,226)
DAK_PINK = (199,21,133)
BLACK = (0,0,0)
IDLE_COLOR = (0,0,0)

BLOCK_COLORS = (240, 249, 242)

COLORS = [DAK_RED , FIS_RED , DAK_YELLOW , SPRINT_GREEN , FOREST , OCEAN , DAK_BLUE , DAK2_BLUE , VIOLET , DAK_PINK]


BLOCK_SPRITE = pygame.sprite.Group()
BS_SPRITE = pygame.sprite.Group()
CAR_SPRITE = pygame.sprite.Group()
BLOCK_array = []
BS_array = []
CAR_array = []


def draw_text(text, font_size, x, y, color):
    FONT = pygame.font.match_font('bitstreamverasans')
    font = pygame.font.Font(FONT, font_size)
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect()
    rect.centerx = x
    rect.centery = y
    screen.blit(text_obj, rect)
    
def CHECK_CAR_TURN():
    for index , car in enumerate(CAR_array):
        x = car.rect.x
        y = car.rect.y
        for i in range(1,10):
            for j in range(1,10):
                tx = BLOCK_SIZE[0] * j + ROAD_SIZE * (j-1)
                ty = BLOCK_SIZE[1] * i + ROAD_SIZE * (i-1)
                if(car.has_turn == False and tx == x and ty == y):                    # 要轉向
                    car.has_turn = True
                    proc = random.randint(0,32)
                    if(proc < 16):
                        pass
                    elif(proc < 24):
                        car.direct += 2
                    elif(proc < 28):
                        car.direct -= 1
                    else:
                        car.direct += 1
                    car.direct %= 4
                else:
                    car.has_turn = False
def CHECK_CAR_REMOVE():
    for i , car in enumerate(CAR_array):
        if(car.rect.x < 0 - ROAD_SIZE or car.rect.x > MAP_SIZE[0] or car.rect.y > MAP_SIZE[1] or car.rect.y < 0 - ROAD_SIZE):
            car.kill()
            CAR_array.remove(car)
def check_interval(start,end,interval):
    for i , j in interval:
        if(end < i):
            continue
        elif(start > j):
            continue
        else:
            return False
    return True
def CHECK_CAR_CALL():
    for car in CAR_array:
        if(car.count_time == 3600):
            car.count_time = 0
        if(car.count_time == 0):
            call = round( random.gauss(mu = 2, sigma = 2) )
            while(call >= 0):
                hold_time = round( random.gauss(mu = 180, sigma = 60) )
                start_time = random.randint(0 , 3600 - hold_time)
                end_time = start_time + hold_time
                if(check_interval(start_time , end_time , car.call_interval)):
                    car.call_interval.append( (start_time , end_time) )    
                    call -= 1
            if(len(car.call_interval) != 0):            
                car.call_interval.sort(key = lambda x:x[0])

            
        if(len(car.call_interval) != 0):
            if(car.count_time == car.call_interval[0][0]):
                car.is_call = True
            elif(car.count_time == car.call_interval[0][1]):
                car.is_call = False
                car.call_interval.pop(0)
        car.count_time = car.count_time + 1
                
def IF_NEED_CREATE():
    poisson = ((LAMBDA * 1) ** 1) * (math.e ** -(LAMBDA * 1))   
    poisson = round(poisson,5) * 100000
    probability = random.randint(0,100000)
    if(probability < poisson):
        return True
    else:
        return False

class BLOCK_t(pygame.sprite.Sprite):                      # BLOCK代表基地台的地基 (繼承了pygame的sprite ， sprite是在pygame裡用於表達物件的一種類別)
    def __init__(self,x,y):                             # 開始設定建構子
        pygame.sprite.Sprite.__init__(self)             # 首先使用sprite內建的建構子
        self.image = pygame.Surface(BLOCK_SIZE)         # 接著設定image，這裡的Surface代表是一個平面。
        self.color = BLOCK_COLORS
        self.image.fill(BLOCK_COLORS)                         # 設定image色碼
        self.rect = self.image.get_rect()               # 讓rect變成是代表物件在視窗中的座標位置

        self.rect.x = x    # 設定X和Y的座標位置 (以左上角為基準)
        self.rect.y = y
    
    def update(self):
        return

class BS_t(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(BS_SIZE)
        color_index = random.randrange(0,10)
        self.color = COLORS[color_index]
        self.frequency = (color_index+1) * 100
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #print(self.rect.x , self.rect.y)
        #print(i,j)
        prob = random.randrange(0,4)
        if prob == 0: #left
            self.rect.x = self.rect.x - 0.1*KM_RATIO
        elif prob == 1: #right
            self.rect.x = self.rect.x + 0.1*KM_RATIO
        elif prob == 2: #up
            self.rect.y = self.rect.y + 0.1*KM_RATIO
        elif prob == 3: #down
            self.rect.y = self.rect.y - 0.1*KM_RATIO
                    
    def update(self):
        return
class CAR_t(pygame.sprite.Sprite):
    def __init__(self,x,y,direct):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((ROAD_SIZE , ROAD_SIZE))
        self.count_time = 0
        self.color = [ IDLE_COLOR , IDLE_COLOR , IDLE_COLOR , IDLE_COLOR]
        self.image.fill(self.color[0])
        self.direct = direct
        self.has_turn = False
        self.rect = self.image.get_rect()
        self.call_interval = []
        self.float_x = float(x)
        self.float_y = float(y)
        self.connect = [-1 , -1, -1, -1]
        self.is_call = False
        self.DB = [-9999 , -9999 , -9999 , -9999]
        self.rect.x = x
        self.rect.y = y
    def update(self):
        if(self.direct == 0):       #往上跑
            self.float_y -= SPEED 
            self.rect.y = round(self.float_y)
        elif(self.direct == 1):     #往右跑
            self.float_x += SPEED 
            self.rect.x = round(self.float_x)
        elif(self.direct == 2):     #往下跑
            self.float_y += SPEED 
            self.rect.y = round(self.float_y)
        else:                       #往左跑
            self.float_x -= SPEED 
            self.rect.x = round(self.float_x)
        
def Create_BLOCK():
    for i in range(10):
        for j in range(10):
            x = (BLOCK_SIZE[0]+ROAD_SIZE) * i
            y = (BLOCK_SIZE[1]+ROAD_SIZE) * j 
            BLOCK = BLOCK_t(x,y);
            BLOCK_SPRITE.add(BLOCK);
            if(random.randrange(0,10) == 0):
                x = ( (BLOCK_SIZE[0]+ROAD_SIZE) * i) + (BLOCK_SIZE[0]-BS_SIZE[0])/2
                y = ( (BLOCK_SIZE[1]+ROAD_SIZE) * j) + (BLOCK_SIZE[1]-BS_SIZE[0])/2
                BS = BS_t(x,y);
                BS_array.append(BS)
                BS_SPRITE.add(BS)
def Create_CAR():
    for direct in range(4):
        for i in range(1,10):
            if(IF_NEED_CREATE()):
                if(direct==0):          # 往上跑
                    x = BLOCK_SIZE[0]*i + ROAD_SIZE*(i-1)
                    y = MAP_SIZE[1]
                elif(direct==1):        # 往右跑
                    x = 0 - ROAD_SIZE
                    y = BLOCK_SIZE[1]*i + ROAD_SIZE*(i-1)
                elif(direct==2):        # 往下跑
                    x = BLOCK_SIZE[0]*i + ROAD_SIZE*(i-1)
                    y = 0 - ROAD_SIZE
                else:                  # 往左跑
                    x = MAP_SIZE[0]
                    y = BLOCK_SIZE[1]*i + ROAD_SIZE*(i-1)
                CAR = CAR_t (x,y,direct)
                CAR_array.append(CAR)
                CAR_SPRITE.add(CAR)
            else:
                continue
def Restart():
    for car in CAR_array:
        car.kill()
    CAR_array.clear()
    global total_switch
    total_switch = [0 , 0 , 0 , 0]
    
def Check_DB(Max_DB , Car_DB):
    if(Car_DB >= Max_DB):
        return False
    elif(Car_DB < MyAlgorithm_MIN_THREADHOLD):
        return True
    elif(Max_DB - Car_DB > MyAlgorithm_error_THRESHOLD):
        return True
    else:
        return False
    
def Check_Algorithm_And_Change(mode , CAR_DB , MAX_DB):
    if(mode == 1):            # Minium
        return CAR_DB < Minium_Pmin
    elif(mode == 2):          # Best-effort
        return True
    elif(mode == 3):          # Entropy
        return MAX_DB - CAR_DB > Entropy_THRESHOLD
    elif(mode == 4):          # MyAlgorithm
        return Check_DB(MAX_DB , CAR_DB)
        
def Update_Connect(index):
    for car in CAR_array:        
        if(car.is_call == False):
            continue
        if(index == 3):          # MyAlgorithm
            tx = car.rect.x
            ty = car.rect.y
            if(car.direct == 0): # up
                ty = 0 - ROAD_SIZE
            elif(car.direct == 1): # right
                tx = MAP_SIZE[0]
            elif(car.direct == 2): # down
                ty = MAP_SIZE[1]
            elif(car.direct == 3):  # left
                tx = 0 - ROAD_SIZE
     
        MAX_DB = car.DB[index]
        BS_index = car.connect[index]
        for i , BS in enumerate(BS_array):
            distance = ((BS.rect.x - car.rect.x)**2 + (BS.rect.y - car.rect.y)**2 ) **0.5 / KM_RATIO
            path_loss =  32.45 + (20 * math.log10(BS.frequency)) + (20 * math.log10(distance))
            Receive_DB = 120 - path_loss
            if(Receive_DB > MAX_DB):
                MAX_DB = Receive_DB
                BS_index = i
            if(i == car.connect[index]):
                car.DB[index] = Receive_DB
                
        if(index == 3):
            if (car.DB[index] < Minium_Pmin):
                Find_BS = False
                for i , BS in enumerate(BS_array):
                    if(Find_BS):
                        break
                    distance = ((BS.rect.x - car.rect.x)**2 + (BS.rect.y - car.rect.y)**2 ) **0.5 / KM_RATIO
                    path_loss =  32.45 + (20 * math.log10(BS.frequency)) + (20 * math.log10(distance))
                    Receive_DB = 120 - path_loss
                    if(Receive_DB > Minium_Pmin):
                        distance2 = ((BS.rect.x - tx)**2 + (BS.rect.y - ty)**2 ) **0.5 / KM_RATIO
                        path_loss2 =  32.45 + (20 * math.log10(BS.frequency)) + (20 * math.log10(distance2))
                        Receive_DB2 = 120 - path_loss2
                        if(Receive_DB2 > Minium_Pmin):
                            Find_BS = True
                            if(car.connect[index] != -1 and car.connect[index] != i):
                                total_switch[index] += 1
                            car.connect[index] = i
                            car.DB[index] = Receive_DB
                            car.color[index] = BS.color
                            if(index == Algorithm_mode):
                                car.image.fill(car.color[index])
                            
                if Find_BS != True:
                    if (BS_index != car.connect[index]):
                        if(car.connect[index] != -1):
                            total_switch[index] += 1
                        car.connect[index] = BS_index
                        car.DB[index] = MAX_DB
                        car.color[index] = BS_array[BS_index].color
                        if(index == Algorithm_mode):
                            car.image.fill(car.color[index])

        else:
            if (BS_index != car.connect[index]):
                if(Check_Algorithm_And_Change(index+1 , car.DB[index] , MAX_DB)):
                    if(car.connect[index] != -1):
                        total_switch[index] += 1
                    car.connect[index] = BS_index
                    car.DB[index] = MAX_DB
                    car.color[index] = BS_array[BS_index].color
                    if(index == Algorithm_mode):
                        car.image.fill(car.color[index])
        
        
def Update_Link():
    if(vision_link == True and vision_car == True):
        for car in CAR_array:
            if(car.is_call == False):
                car.color[Algorithm_mode-1] = IDLE_COLOR
                car.image.fill(car.color[Algorithm_mode-1])
                continue
            BS = BS_array[car.connect[Algorithm_mode-1]]
            car.color[Algorithm_mode-1] = BS.color
            car.image.fill(car.color[Algorithm_mode-1])
            pygame.draw.line(screen , car.color[Algorithm_mode-1] , (car.rect.centerx , car.rect.centery) , (BS.rect.centerx , BS.rect.centery) , 1)
def Update_Text():
    if(vision_db == True and vision_car == True) :
        for car in CAR_array:
            if(car.is_call):
                number = round(car.DB[Algorithm_mode-1],1)
                text = str(number) + " db"
                draw_text(text , 14 , car.rect.centerx , car.rect.centery-13 , BLACK)
    
    for BS in BS_array:
        text = str(BS.frequency) + "Mhz"
        draw_text(text , 17 , BS.rect.centerx , BS.rect.centery , BLACK)

    text = "Minimum Switch = " + str(total_switch[0])
    draw_text(text , 40 , MAP_SIZE[0] + 200 , 50 , BLACK)
    text = "Best-effort Switch = " + str(total_switch[1])
    draw_text(text , 40 , MAP_SIZE[0] + 200 , 120 , BLACK)
    text = "Entropy Switch = " + str(total_switch[2])
    draw_text(text , 40 , MAP_SIZE[0] + 200 , 190 , BLACK)
    text = "Minimum_stock Switch = " + str(total_switch[3])
    draw_text(text , 40 , MAP_SIZE[0] + 200 , 260 , BLACK)
    text = "Total Car = " + str(len(CAR_array))
    draw_text(text , 40 , MAP_SIZE[0] + 180 , 330 , BLACK)
    text = "Car Speed = " + str(KM_SPEED *3600) + "km/hr"
    draw_text(text , 35 , MAP_SIZE[0] + 240 , 500 , BLACK)
    text = "Lambda = " + str(round(LAMBDA*60 , 2)) + " cars / min"
    draw_text(text , 35 , MAP_SIZE[0] + 250 , 570 , BLACK)
    
    if(Algorithm_mode == 1):
        text = "Algorithm : Minimum"
    elif(Algorithm_mode == 2):
        text = "Algorithm : Best-effort"
    elif(Algorithm_mode == 3):
        text = "Algorithm : Entropy"
    elif(Algorithm_mode == 4):
        text = "Algorithm : Minimum_stock"
    draw_text(text , 35 , MAP_SIZE[0] + 250 , 700 , BLACK)
    
    if(filter_idle_car):
        text = "Filter Idle Car : On"
        draw_text(text , 40 , MAP_SIZE[0] + 250 , 600 , BLACK)
def Pygame_Initial():
    pygame.init()
    pygame.display.set_caption("BEST_EFFORT")
    global screen  
    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(WHITE)
    global clock
    clock = pygame.time.Clock()
    
    global total_switch 
    total_switch = [0 , 0 , 0 , 0]
def Sprite_Initial():
    return
if __name__ == "__main__":
    Pygame_Initial()
    Sprite_Initial()
    Create_BLOCK()
    

    while RUNNING == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if(event.key == pygame.K_z):
                    vision_db = not vision_db
                elif(event.key == pygame.K_x):
                    vision_link = not vision_link
                elif(event.key == pygame.K_c):
                    vision_car = not vision_car
                elif(event.key == pygame.K_v):
                    filter_idle_car = not filter_idle_car
                elif(event.key == pygame.K_SPACE):
                    Restart()
                elif(event.key == pygame.K_RIGHT):
                    KM_SPEED *= 2
                elif(event.key == pygame.K_LEFT):
                    KM_SPEED /= 2
                elif(event.key == pygame.K_UP):
                    LAMBDA *= 2
                elif(event.key == pygame.K_DOWN):
                    LAMBDA /= 2
                elif(event.key == pygame.K_1):
                    Algorithm_mode = 1
                    pygame.display.set_caption("MINIMUM")
                elif(event.key == pygame.K_2):
                    Algorithm_mode = 2
                    pygame.display.set_caption("BEST_EFFORT")
                elif(event.key == pygame.K_3):
                    pygame.display.set_caption("ENTROPY")
                    Algorithm_mode = 3
                elif(event.key == pygame.K_4):
                    pygame.display.set_caption("Minium_stock")
                    Algorithm_mode = 4
                
                    

        FONT = pygame.font.match_font('bitstreamverasans')

        clock.tick(FPS_FRAME)
        
        Create_CAR()
        screen.fill(WHITE)
        BLOCK_SPRITE.draw(screen)
        BS_SPRITE.draw(screen)
        if(vision_car == True):
            if(filter_idle_car == True):
                for car in CAR_array:
                    if(car.is_call):
                        screen.blit(car.image , car.rect)
            else:
                CAR_SPRITE.draw(screen) 
        SPEED = KM_SPEED * KM_RATIO
        CHECK_CAR_REMOVE()
        CHECK_CAR_TURN()
        CHECK_CAR_CALL()
        for i in range(4):
            Update_Connect(i)        
        Update_Link()
        Update_Text()
        BS_SPRITE.update()
        BLOCK_SPRITE.update()
        CAR_SPRITE.update()
        pygame.display.update()
        
    pygame.quit()