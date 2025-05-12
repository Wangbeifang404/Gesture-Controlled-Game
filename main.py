
"""
手势控制躲避游戏 - 主程序入口
整合手势识别和游戏逻辑模块
"""

import pygame
from game import DodgeGame
from gesture_detect import GestureRecognizer

def main():
    """
    游戏主函数
    初始化游戏并运行主循环
    """
    try:
        # 初始化游戏实例
        game = DodgeGame(width=800, height=600, cam_width=200)
        
        # 运行游戏
        game.run()
        
    except Exception as e:
        print(f"游戏运行出错: {e}")
    finally:
        # 确保资源释放
        game.release()

if __name__ == "__main__":
    # 启动游戏
    main()
