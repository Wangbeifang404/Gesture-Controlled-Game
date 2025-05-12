
"""
游戏核心逻辑模块
包含游戏状态管理、界面渲染和游戏规则实现
"""

import pygame
import random
import numpy as np
import cv2
from gesture_detect import GestureRecognizer

class DodgeGame:
    """
    躲避障碍物游戏类
    
    属性:
    - width, height: 游戏窗口尺寸
    - game_width: 游戏区域宽度
    - colors: 游戏配色方案
    - player: 玩家角色属性
    - obstacles: 障碍物列表
    - game_state: 游戏状态变量
    - recognizer: 手势识别器实例
    """
    
    def __init__(self, width=800, height=600, cam_width=200):
        """初始化游戏"""
        pygame.init()
        
        # 窗口设置
        self.width = width
        self.height = height
        self.game_width = width - cam_width
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("手势控制躲避游戏")
        
        # 颜色定义
        self.colors = {
            'white': (255, 255, 255),
            'red': (255, 80, 80),
            'blue': (100, 150, 255),
            'black': (30, 30, 40),
            'gray': (100, 100, 120),
            'green': (100, 255, 100)
        }
        
        # 玩家设置
        self.player = {
            'radius': 20,
            'x': self.game_width // 2,
            'y': height - 50,
            'speed': 5
        }
        
        # 障碍物设置
        self.obstacles = []
        self.obstacle_speed = 3
        self.obstacle_frequency = 60  # 生成频率(帧数)
        
        # 游戏状态
        self.game_over = False
        self.score = 0
        self.frame_count = 0
        self.clock = pygame.time.Clock()
        
        # 手势识别器
        self.recognizer = None
        
        # 初始化字体
        try:
            self.score_font = pygame.font.Font("simhei.ttf", 32)  # 分数字体
            self.gesture_font = pygame.font.Font("simhei.ttf", 28)  # 手势提示字体
            self.game_over_font = pygame.font.Font("simhei.ttf", 64)  # 游戏结束字体
        except:
            self.score_font = pygame.font.SysFont("microsoftyahei", 32)
            self.gesture_font = pygame.font.SysFont("microsoftyahei", 28)
            self.game_over_font = pygame.font.SysFont("microsoftyahei", 64)
            
        # 文字颜色
        self.text_colors = {
            'score': (255, 255, 150),  # 分数文字(浅黄色)
            'gesture': (180, 255, 180),  # 手势提示(浅绿色)
            'game_over': (255, 100, 100)  # 游戏结束(浅红色)
        }

    def init_recognizer(self):
        """初始化手势识别器"""
        self.recognizer = GestureRecognizer()
        
    def draw_player(self):
        """绘制玩家角色"""
        pygame.draw.circle(
            self.screen, 
            self.colors['blue'],
            (self.player['x'], self.player['y']),
            self.player['radius']
        )
    
    def create_obstacle(self):
        """创建新的障碍物"""
        width = random.randint(50, 100)
        return {
            'x': random.randint(0, self.game_width - width),
            'y': -20,
            'width': width,
            'height': 20,
            'speed': self.obstacle_speed
        }

    def draw_obstacles(self):
        """绘制所有障碍物"""
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen,
                self.colors['red'],
                (obstacle['x'], obstacle['y'], 
                 obstacle['width'], obstacle['height'])
            )

    def check_collision(self):
        """检测玩家与障碍物碰撞"""
        for obstacle in self.obstacles:
            if (self.player['y'] - self.player['radius'] < obstacle['y'] + obstacle['height'] and
                self.player['y'] + self.player['radius'] > obstacle['y'] and
                self.player['x'] + self.player['radius'] > obstacle['x'] and
                self.player['x'] - self.player['radius'] < obstacle['x'] + obstacle['width']):
                return True
        return False

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                
        # 手势控制
        if self.recognizer:
            gesture = self.recognizer.get_gesture()
            if gesture == "左滑" and self.player['x'] > self.player['radius']:
                self.player['x'] -= self.player['speed']
            elif gesture == "右滑" and self.player['x'] < self.game_width - self.player['radius']:
                self.player['x'] += self.player['speed']
        
        # 键盘控制(备用)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player['x'] > self.player['radius']:
            self.player['x'] -= self.player['speed']
        if keys[pygame.K_RIGHT] and self.player['x'] < self.game_width - self.player['radius']:
            self.player['x'] += self.player['speed']

    def update(self):
        """更新游戏状态"""
        # 生成障碍物
        self.frame_count += 1
        if self.frame_count % self.obstacle_frequency == 0:
            self.obstacles.append(self.create_obstacle())
        
        # 更新障碍物位置
        for obstacle in self.obstacles[:]:
            obstacle['y'] += obstacle['speed']
            if obstacle['y'] > self.height:
                self.obstacles.remove(obstacle)
                self.score += 1
        
        # 提高难度
        if self.score > 0 and self.score % 10 == 0:
            self.obstacle_speed = 3 + self.score // 10
            self.obstacle_frequency = max(30, 60 - self.score // 5)
        
        # 检测碰撞
        if self.check_collision():
            self.game_over = True

    def render(self):
        """渲染游戏画面"""
        # 绘制渐变背景
        self.screen.fill(self.colors['black'])
        for y in range(self.height):
            color = (
                max(0, min(50, y//10)), 
                max(0, min(70, y//12)), 
                max(0, min(90, y//8))
            )
            pygame.draw.line(self.screen, color, (0, y), (self.game_width, y))
        
        # 绘制游戏元素
        self.draw_player()
        self.draw_obstacles()
        
        # 绘制分数（无边框）
        score_text = self.score_font.render(f"分数: {self.score}", True, self.text_colors['score'])
        self.screen.blit(score_text, (20, 20))
        
        # 绘制摄像头预览
        if self.recognizer:
            self.render_camera_preview()
        
        pygame.display.flip()
        self.clock.tick(60)

    def render_camera_preview(self):
        """渲染摄像头预览画面"""
        ret, frame = self.recognizer.cap.read()
        if ret:
            # 保持比例的预览窗口
            h, w = frame.shape[:2]
            aspect_ratio = w / h
            preview_height = int((self.width - self.game_width - 20) / aspect_ratio)
            preview_height = min(preview_height, 400)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.width - self.game_width - 20, preview_height))
            frame = pygame.surfarray.make_surface(frame.swapaxes(0,1))
            
            # 添加边框
            pygame.draw.rect(
                self.screen, 
                self.colors['gray'], 
                (self.game_width+8, 8, self.width-self.game_width-4, preview_height+4), 
                2, border_radius=8
            )
            self.screen.blit(frame, (self.game_width+10, 10))
            
            # 显示手势方向
            if self.recognizer.last_gesture:
                self.render_gesture_hint(preview_height)

    def render_gesture_hint(self, preview_height):
        """渲染手势提示"""
        direction_box_height = 50
        pygame.draw.rect(
            self.screen, 
            self.colors['gray'],
            (self.game_width+8, preview_height+12, 
             self.width-self.game_width-4, direction_box_height), 
            0, border_radius=8
        )
        gesture_text = self.gesture_font.render(
            f"当前手势: {self.recognizer.last_gesture}", 
            True, 
            self.text_colors['gesture']
        )
        text_rect = gesture_text.get_rect(
            center=(self.game_width+(self.width-self.game_width)//2, 
                   preview_height+12+direction_box_height//2)
        )
        self.screen.blit(gesture_text, text_rect)

    def reset_game(self):
        """重置游戏状态"""
        self.player['x'] = self.game_width // 2
        self.game_over = False
        self.frame_count = 0
        self.obstacle_speed = 3
        self.obstacle_frequency = 60
        self.score = 0
        self.obstacles = []

    def game_over_screen(self):
        """显示游戏结束画面"""
        # 确保截图目录存在
        import os
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # 生成带时间戳的截图文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/{timestamp}.png"
        
        # 保存当前画面为截图
        pygame.image.save(self.screen, screenshot_path)
        
        end_active = True
        restart_button = pygame.Rect(self.width//2-220, self.height//2+50, 200, 50)
        quit_button = pygame.Rect(self.width//2+20, self.height//2+50, 200, 50)
        
        while end_active:
            self.screen.fill(self.colors['black'])
            
            # 绘制渐变背景
            for y in range(self.height):
                color = (max(0, min(50, y//10)), max(0, min(30, y//15)), max(0, min(20, y//20)))
                pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
            # 绘制游戏结束文字
            text = self.game_over_font.render("游戏结束", True, self.text_colors['game_over'])
            text_rect = text.get_rect(center=(self.width//2, self.height//3))
            self.screen.blit(text, text_rect)
            
            # 绘制分数
            score_text = self.score_font.render(f"最终分数: {self.score}", True, self.text_colors['score'])
            score_rect = score_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(score_text, score_rect)
            
            # 绘制重新开始按钮
            pygame.draw.rect(self.screen, self.colors['green'], restart_button, 0, border_radius=10)
            pygame.draw.rect(self.screen, self.colors['white'], restart_button, 2, border_radius=10)
            restart_text = self.score_font.render("重新开始", True, self.colors['black'])
            restart_rect = restart_text.get_rect(center=restart_button.center)
            self.screen.blit(restart_text, restart_rect)
            
            # 绘制退出按钮
            pygame.draw.rect(self.screen, self.colors['red'], quit_button, 0, border_radius=10)
            pygame.draw.rect(self.screen, self.colors['white'], quit_button, 2, border_radius=10)
            quit_text = self.score_font.render("退出游戏", True, self.colors['black'])
            quit_rect = quit_text.get_rect(center=quit_button.center)
            self.screen.blit(quit_text, quit_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_active = False
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        end_active = False
                        return True
                    if quit_button.collidepoint(event.pos):
                        end_active = False
                        return False
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return True

    def show_start_menu(self):
        """显示开始菜单"""
        menu_active = True
        start_button = pygame.Rect(self.width//2-100, self.height//2, 200, 50)
        
        while menu_active:
            self.screen.fill(self.colors['black'])
            
            # 绘制渐变背景
            for y in range(self.height):
                color = (max(0, min(30, y//15)), max(0, min(50, y//12)), max(0, min(70, y//10)))
                pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
            # 绘制标题
            title_text = self.game_over_font.render("手势躲避游戏", True, self.colors['blue'])
            title_rect = title_text.get_rect(center=(self.width//2, self.height//3))
            self.screen.blit(title_text, title_rect)
            
            # 绘制游戏说明
            instruction = self.gesture_font.render("使用左右手势控制小球移动", True, self.colors['white'])
            instr_rect = instruction.get_rect(center=(self.width//2, self.height//2-50))
            self.screen.blit(instruction, instr_rect)
            
            # 绘制开始按钮
            pygame.draw.rect(self.screen, self.colors['green'], start_button, 0, border_radius=10)
            pygame.draw.rect(self.screen, self.colors['white'], start_button, 2, border_radius=10)
            start_text = self.score_font.render("开始游戏", True, self.colors['black'])
            start_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_rect)
            
            # 添加水印
            watermark_font = pygame.font.SysFont("microsoftyahei", 16)
            watermark = watermark_font.render("王鑫 2020211837", True, (150, 150, 150, 128))
            self.screen.blit(watermark, (self.width - 150, self.height - 30))
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        menu_active = False
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return True

    def run(self):
        """运行游戏主循环"""
        if not self.recognizer:
            self.init_recognizer()
            
        # 显示开始菜单
        if not self.show_start_menu():
            return
            
        self.reset_game()
        
        while not self.game_over:
            self.handle_events()
            self.update()
            self.render()
            
        if self.game_over_screen():  # 如果选择重新开始
            self.run()

    def release(self):
        """释放资源"""
        if self.recognizer:
            self.recognizer.release()
        pygame.quit()

if __name__ == "__main__":
    """模块测试代码"""
    game = DodgeGame()
    try:
        game.run()
    finally:
        game.release()
