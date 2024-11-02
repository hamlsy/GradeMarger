# game_objects.py
import pygame
import pymunk
import random
from config import *

class GradeBall:
    def __init__(self, space, pos, grade):
        # 성적 정보 설정
        self.grade = grade
        self.color = GRADES[grade]['color']
        self.size = GRADES[grade]['size']
        
        # 물리 바디 생성
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, self.size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        
        # 물리 형태 생성
        self.shape = pymunk.Circle(self.body, self.size)
        self.shape.friction = BALL_FRICTION
        self.shape.elasticity = BALL_ELASTICITY
        self.shape.collision_type = 1
        self.shape.grade_obj = self
        
        # 공간에 추가
        space.add(self.body, self.shape)
        
        # 드롭 상태
        self.dropped = False
    
    @staticmethod
    def create_random_grade(space, pos, round_num=1):
        # 라운드에 따라 등장할 수 있는 성적 결정
        available_grades = ['F', 'D']
        if round_num > 5:
            available_grades.append('C')
        
        grade = random.choice(available_grades)
        return GradeBall(space, pos, grade)
    
    def drop(self):
        # 공을 떨어뜨림
        self.dropped = True
        self.body.body_type = pymunk.Body.DYNAMIC
    
    def draw(self, screen):
        # 화면에 공 그리기
        pos = self.body.position
        pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.size)
        
        # 성적 텍스트 그리기
        font = pygame.font.SysFont(None, 30)
        text = font.render(self.grade, True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(pos.x), int(pos.y)))
        screen.blit(text, text_rect)

class Item:
    def __init__(self, space, pos, item_type):
        # 아이템 정보 설정
        self.item_type = item_type
        self.color = ITEMS[item_type]['color']
        self.size = ITEMS[item_type]['size']
        
        # 물리 바디 생성
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, self.size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        
        # 물리 형태 생성
        self.shape = pymunk.Circle(self.body, self.size)
        self.shape.friction = BALL_FRICTION
        self.shape.elasticity = BALL_ELASTICITY
        self.shape.collision_type = 2
        self.shape.item_obj = self
        
        # 공간에 추가
        space.add(self.body, self.shape)
    
    @staticmethod
    def create_random_item(space, pos):
        # 랜덤으로 아이템 생성
        items = list(ITEMS.keys())
        probabilities = [ITEMS[item]['probability'] for item in items]
        
        if random.random() < sum(probabilities):
            item_type = random.choices(items, probabilities)[0]
            return Item(space, pos, item_type)
        return None
    
    def draw(self, screen):
        # 화면에 아이템 그리기
        pos = self.body.position
        pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.size)
        
        # 아이템 텍스트 그리기
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.item_type, True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(pos.x), int(pos.y)))
        screen.blit(text, text_rect)
