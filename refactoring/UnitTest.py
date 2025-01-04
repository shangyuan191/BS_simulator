import unittest
import pygame
import math
from unittest.mock import Mock, patch
from game import Game
from sprites import Car, BS, BG, Explosion_X
import config

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.config = config.Config()
        
    def test_calculate_dis(self):
        # distance = self.game.calculate_dis(0, 0, 3, 4)
        # self.assertEqual(distance, 5.0)
        """測試距離計算函數"""
        # 測試基本距離計算
        self.assertEqual(self.game.calculate_dis(0, 0, 3, 4), 5)
        self.assertEqual(self.game.calculate_dis(1, 1, 4, 5), 5)
        
        # 測試相同點的距離
        self.assertEqual(self.game.calculate_dis(10, 10, 10, 10), 0)
        
        # 測試負數座標
        self.assertAlmostEqual(self.game.calculate_dis(-1, -1, 2, 2), 4.242640687119285)
        
    def test_calculate_DB(self):
        # # Testing DB calculation with known values
        # freq = 1000  # 1000 MHz
        # dis = 1      # 1 km
        # expected_db = self.game.config.PT - (32.45 + 20 * math.log(freq, 10) + 20 * math.log(dis, 10))
        # self.assertAlmostEqual(self.game.calculate_DB(freq, dis), expected_db)
        """測試分貝計算函數"""
        # 測試基本分貝計算
        freq = 100  # MHz
        dis = 1     # km
        expected_db = self.config.PT - (32.45 + 20 * math.log(freq, 10) + 20 * math.log(dis, 10))
        self.assertAlmostEqual(self.game.calculate_DB(freq, dis), expected_db)
        
        # 測試不同距離的衰減
        self.assertGreater(self.game.calculate_DB(freq, 1), self.game.calculate_DB(freq, 2))  

    def test_car_creation(self):
        initial_car_count = len(self.game.carsprites)
        car = Car(0, 50, 1, (255,0,0), self.game.explosion_and_new_born)
        self.game.car_create(car)
        self.assertEqual(len(self.game.carsprites), initial_car_count + 1)
        """測試車輛類的創建和初始化"""
        # 測試向上移動的車輛
        car_up = Car(100, 100, 0, (255, 0, 0), self.game.explosion_and_new_born)
        self.assertEqual(car_up.speedx, 0)
        self.assertEqual(car_up.speedy, -self.config.V)
        
        # 測試向右移動的車輛
        car_right = Car(100, 100, 1, (255, 0, 0), self.game.explosion_and_new_born)
        self.assertEqual(car_right.speedx, self.config.V)
        self.assertEqual(car_right.speedy, 0)
        
        # 測試初始位置
        self.assertEqual(car_up.rect.x, 100)
        self.assertEqual(car_up.rect.y, 100)

    def test_explosion_and_new_born(self):
        car = Car(0, 50, 1, (255,0,0), self.game.explosion_and_new_born)
        self.game.car_create(car)
        initial_car_count = len(self.game.carsprites)
        self.game.explosion_and_new_born(car)
        self.assertEqual(len(self.game.carsprites), initial_car_count - 1)

class TestCarMechanics(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.car = Car(50, 50, 1, (255,0,0), self.game.explosion_and_new_born)
        
    def test_car_movement(self):
        initial_x = self.car.rect.x
        initial_y = self.car.rect.y
        self.car.update()
        # Car moving right (direction 1)
        self.assertGreater(self.car.rect.x, initial_x)
        self.assertEqual(self.car.rect.y, initial_y)
        
    def test_car_direction_change(self):
        # Force car to intersection point
        self.car.rect.x = self.game.config.BLOCK_SIZE + 10
        self.car.rect.y = self.game.config.BLOCK_SIZE + 10
        original_direction = self.car.direction
        self.car.update()
        # Direction might change at intersection
        self.assertIn(self.car.direction, [0, 1, 2, 3])

class TestBSMechanics(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.config = config.Config()
        
    def test_bs_load_calculation(self):
        # Test best effort load calculation
        if len(self.game.BS_sprites) > 0:
            bs = self.game.BS_sprites[0]
            initial_load = bs.load_car_best_effort
            car = Car(bs.rect.x, bs.rect.y, 1, (255,0,0), self.game.explosion_and_new_born)
            self.game.car_create(car)
            self.game.update_best_effort(car)
            self.assertGreater(bs.load_car_best_effort, initial_load)
            
    def test_handover_mechanics(self):
        if len(self.game.BS_sprites) >= 2:
            car = Car(0, 50, 1, (255,0,0), self.game.explosion_and_new_born)
            self.game.car_create(car)
            initial_bs = car.BS_best_effort
            # Move car closer to another BS
            car.rect.x = self.game.BS_sprites[1].rect.x
            car.rect.y = self.game.BS_sprites[1].rect.y
            self.game.update_best_effort(car)
            # Check if handover occurred
            self.assertNotEqual(car.BS_best_effort, initial_bs)

    def test_bs_creation(self):
        """測試基地台類的創建和初始化"""
        bs = BS(100, 100,self.game.bg_image)
        
        # 測試基地台位置計算
        base_x = 100 + ((self.config.BLOCK_SIZE - self.config.BS_SIZE) / 2)
        base_y = 100 + ((self.config.BLOCK_SIZE - self.config.BS_SIZE) / 2)
        
        # 考慮偏移量
        offset = self.config.BLOCK_SIZE/25
        
        # 檢查位置是否在預期範圍內
        self.assertTrue(
            abs(bs.rect.x - base_x) <= offset,
            f"X position {bs.rect.x} is not within expected range of {base_x} ± {offset}"
        )
        self.assertTrue(
            abs(bs.rect.y - base_y) <= offset,
            f"Y position {bs.rect.y} is not within expected range of {base_y} ± {offset}"
        )
        
        # 測試初始負載計數
        self.assertEqual(bs.load_car_best_effort, 0)
        self.assertEqual(bs.load_car_minimum_threshold, 0)
        self.assertEqual(bs.load_car_entropy, 0)
        self.assertEqual(bs.load_car_admission_nearby, 0)

    def test_distance_calculations(self):
        """測試實際場景中的距離計算"""
        car = Car(100, 100, 1, (255, 0, 0),self.game.explosion_and_new_born)
        bs = BS(200, 200,self.game.bg_image)
        
        # 計算實際距離
        distance = self.game.calculate_dis(car.rect.centerx, car.rect.centery,
                               bs.rect.centerx, bs.rect.centery)
        
        # 轉換為公里
        distance_km = distance * self.config.Distance_scaler
        
        # 確認距離計算的合理性
        self.assertTrue(0 < distance_km < 100)  # 假設地圖尺寸合理

class TestSystemMechanics(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.config = config.Config()
        
    def test_mode_switching(self):
        initial_mode = self.game.mode
        # Simulate key press
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_1
        with patch('pygame.event.get', return_value=[event]):
            self.game.handle_events()
        self.assertEqual(self.game.mode, 1)
        
    @patch('random.randrange')
    def test_car_spawn_rate(self, mock_random):
        mock_random.return_value = 0  # Force spawn
        initial_cars = len(self.game.carsprites)
        self.game.car_create_func()
        self.assertGreater(len(self.game.carsprites), initial_cars)
    def test_signal_strength_calculation(self):
        """測試訊號強度計算的整體流程"""
        car = Car(100, 100, 1, (255, 0, 0),self.game.explosion_and_new_born)
        bs = BS(200, 200,self.game.bg_image)
        bs.DBpower = 1000  # 設定基地台功率
        
        # 計算距離和訊號強度
        distance = self.game.calculate_dis(car.rect.centerx, car.rect.centery,
                               bs.rect.centerx, bs.rect.centery)
        signal_strength = self.game.calculate_DB(bs.DBpower, distance * self.config.Distance_scaler)
        
        # 確認訊號強度隨距離衰減
        closer_car = Car(190, 190, 1, (255, 0, 0),self.game.explosion_and_new_born)
        closer_distance = self.game.calculate_dis(closer_car.rect.centerx, closer_car.rect.centery,
                                      bs.rect.centerx, bs.rect.centery)
        closer_signal = self.game.calculate_DB(bs.DBpower, closer_distance * self.config.Distance_scaler)
        
        self.assertGreater(closer_signal, signal_strength)

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()