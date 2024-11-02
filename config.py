# config.py

# 창 설정
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = (240, 240, 240)

# 물리 엔진 설정
GRAVITY = 981.0
BALL_FRICTION = 0.5
BALL_ELASTICITY = 0.5

# 성적 설정
GRADES = {
    'F': {'color': (255, 0, 0), 'size': 30, 'score': 10},
    'D': {'color': (255, 165, 0), 'size': 40, 'score': 20},
    'C': {'color': (255, 255, 0), 'size': 50, 'score': 40},
    'B': {'color': (0, 255, 0), 'size': 60, 'score': 80},
    'A': {'color': (0, 0, 255), 'size': 70, 'score': 160},
    'A+': {'color': (128, 0, 128), 'size': 80, 'score': 320}
}

# 아이템 설정
ITEMS = {
    '과제': {'color': (150, 150, 150), 'size': 35, 'probability': 0.1},
    '휴강': {'color': (255, 192, 203), 'size': 35, 'probability': 0.05}
}

# UI 설정
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 32
