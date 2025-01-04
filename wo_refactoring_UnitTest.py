import unittest
import pygame
import math
from unittest.mock import Mock, patch
from BS_simulator import (
    calculate_dis, calculate_DB, Car, BS, BG,
    Distance_scaler, Pt, BLOCK_SIZE, BS_SIZE, WIDTH, HEIGHT, V
)

class TestBSSimulator(unittest.TestCase):
    def setUp(self):
        """初始化測試環境"""
        pygame.init()
        # 創建一個虛擬的顯示窗口以供測試
        pygame.display.set_mode((800, 600))

    def tearDown(self):
        """清理測試環境"""
        pygame.quit()

    def test_calculate_dis(self):
        """測試距離計算函數"""
        # 測試基本距離計算
        self.assertEqual(calculate_dis(0, 0, 3, 4), 5)
        self.assertEqual(calculate_dis(1, 1, 4, 5), 5)
        
        # 測試相同點的距離
        self.assertEqual(calculate_dis(10, 10, 10, 10), 0)
        
        # 測試負數座標
        self.assertAlmostEqual(calculate_dis(-1, -1, 2, 2), 4.242640687119285)

    def test_calculate_DB(self):
        """測試分貝計算函數"""
        # 測試基本分貝計算
        freq = 100  # MHz
        dis = 1     # km
        expected_db = Pt - (32.45 + 20 * math.log(freq, 10) + 20 * math.log(dis, 10))
        self.assertAlmostEqual(calculate_DB(freq, dis), expected_db)
        
        # 測試不同距離的衰減
        self.assertGreater(calculate_DB(freq, 1), calculate_DB(freq, 2))

    def test_car_creation(self):
        """測試車輛類的創建和初始化"""
        # 測試向上移動的車輛
        car_up = Car(100, 100, 0, (255, 0, 0))
        self.assertEqual(car_up.speedx, 0)
        self.assertEqual(car_up.speedy, -V)
        
        # 測試向右移動的車輛
        car_right = Car(100, 100, 1, (255, 0, 0))
        self.assertEqual(car_right.speedx, V)
        self.assertEqual(car_right.speedy, 0)
        
        # 測試初始位置
        self.assertEqual(car_up.rect.x, 100)
        self.assertEqual(car_up.rect.y, 100)

    def test_car_movement(self):
        """測試車輛移動"""
        car = Car(100, 100, 1, (255, 0, 0))  # 向右移動的車輛
        initial_x = car.rect.x
        initial_y = car.rect.y
        
        # 更新一次位置
        car.update()
        
        # 確認水平移動
        self.assertEqual(car.rect.x, initial_x + V)
        self.assertEqual(car.rect.y, initial_y)

    def test_bs_creation(self):
        """測試基地台類的創建和初始化"""
        bs = BS(100, 100)
        
        # 測試基地台位置計算
        base_x = 100 + ((BLOCK_SIZE - BS_SIZE) / 2)
        base_y = 100 + ((BLOCK_SIZE - BS_SIZE) / 2)
        
        # 考慮偏移量
        offset = BLOCK_SIZE/25
        
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

    def test_bg_creation(self):
        """測試背景區塊的創建"""
        bg = BG(100, 100)
        
        # 測試背景位置
        self.assertEqual(bg.rect.x, 100)
        self.assertEqual(bg.rect.y, 100)
        
        # 測試背景大小
        self.assertEqual(bg.rect.width, BLOCK_SIZE)
        self.assertEqual(bg.rect.height, BLOCK_SIZE)

    def test_car_boundary_collision(self):
        """測試車輛碰到邊界的行為"""
        # 創建一個即將到達右邊界的車輛
        car = Car(WIDTH - 11, 100, 1, (255, 0, 0))
        
        # 模擬精靈組
        with patch('pygame.sprite.Group') as mock_group:
            all_sprites = mock_group.return_value
            car.all_sprites = all_sprites
            
            # 更新位置
            car.update()
            
            # 驗證是否觸發了爆炸動畫
            self.assertTrue(hasattr(car, 'explosion_and_new_born'))

    def test_distance_calculations(self):
        """測試實際場景中的距離計算"""
        car = Car(100, 100, 1, (255, 0, 0))
        bs = BS(200, 200)
        
        # 計算實際距離
        distance = calculate_dis(car.rect.centerx, car.rect.centery,
                               bs.rect.centerx, bs.rect.centery)
        
        # 轉換為公里
        distance_km = distance * Distance_scaler
        
        # 確認距離計算的合理性
        self.assertTrue(0 < distance_km < 100)  # 假設地圖尺寸合理

    def test_signal_strength_calculation(self):
        """測試訊號強度計算的整體流程"""
        car = Car(100, 100, 1, (255, 0, 0))
        bs = BS(200, 200)
        bs.DBpower = 1000  # 設定基地台功率
        
        # 計算距離和訊號強度
        distance = calculate_dis(car.rect.centerx, car.rect.centery,
                               bs.rect.centerx, bs.rect.centery)
        signal_strength = calculate_DB(bs.DBpower, distance * Distance_scaler)
        
        # 確認訊號強度隨距離衰減
        closer_car = Car(190, 190, 1, (255, 0, 0))
        closer_distance = calculate_dis(closer_car.rect.centerx, closer_car.rect.centery,
                                      bs.rect.centerx, bs.rect.centery)
        closer_signal = calculate_DB(bs.DBpower, closer_distance * Distance_scaler)
        
        self.assertGreater(closer_signal, signal_strength)

if __name__ == '__main__':
    unittest.main()