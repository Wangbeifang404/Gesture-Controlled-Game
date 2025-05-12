
"""
手势识别模块
使用MediaPipe实现实时手势检测
功能：
1. 初始化摄像头
2. 检测左右滑动手势
3. 提供摄像头帧预览功能
"""

import cv2
import mediapipe as mp
import numpy as np

class GestureRecognizer:
    """
    手势识别器类
    使用食指位置判断左右滑动方向
    
    属性:
    - hands: MediaPipe手部检测模型
    - cap: 摄像头实例
    - last_gesture: 最后识别到的手势
    """
    
    def __init__(self):
        """初始化手势识别器"""
        # 初始化MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,  # 只检测一只手
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)  # 初始化摄像头
        self.last_gesture = None  # 记录最后一次识别的手势

    def get_gesture(self):
        """
        获取当前手势
        
        返回:
        - "左滑" 或 "右滑": 检测到的手势方向
        - None: 未检测到手势
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # 转换BGR到RGB格式
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        
        if results.multi_hand_landmarks:
            # 获取食指(8)和手腕(0)的坐标
            landmarks = results.multi_hand_landmarks[0].landmark
            index_tip = landmarks[8]
            wrist = landmarks[0]
            
            # 判断左右滑动（考虑镜像）
            if index_tip.x > wrist.x + 0.1:  # 实际向左滑动
                self.last_gesture = "左滑"
                return self.last_gesture
            elif index_tip.x < wrist.x - 0.1:  # 实际向右滑动
                self.last_gesture = "右滑"
                return self.last_gesture
                
        self.last_gesture = None
        return None
        
    def release(self):
        """释放资源"""
        self.hands.close()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    """模块测试代码"""
    recognizer = GestureRecognizer()
    try:
        while True:
            gesture = recognizer.get_gesture()
            if gesture:
                print(f"识别到手势: {gesture}")
                
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    finally:
        recognizer.release()
