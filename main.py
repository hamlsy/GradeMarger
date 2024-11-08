# main.py
# src/main.py
import pygame
import pymunk
import sys
import os

from game_state import GameState
from game_objects import GradeBall, Item
from game_state import UIManager
from game_state import ScoreManager
from collision_handler import CollisionHandler
from game_state import Effects
from config import *


class GradeMerger:
    def __init__(self):
        # Pygame 초기화
        pygame.init()
        pygame.display.set_caption("성적합치기")

        # 화면 설정
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # 물리 엔진 공간 생성
        self.space = pymunk.Space()
        self.space.gravity = (0.0, GRAVITY)

        # 게임 상태 관리자 초기화
        self.game_state = GameState()

        # UI 관리자 초기화
        self.ui_manager = UIManager(self.screen)

        # 점수 관리자 초기화
        self.score_manager = ScoreManager()

        # 벽 경계 생성
        self.create_boundaries()

        # 게임 루프 제어를 위한 변수들
        self.clock = pygame.time.Clock()
        self.current_ball = None
        self.mouse_pos = (WINDOW_WIDTH // 2, 0)

        # 게임 오브젝트 저장소 추가
        self.balls = []  # 현재 게임에 있는 모든 공들을 저장
        self.score = 0  # 현재 점수 저장

    def create_boundaries(self):
        # 바닥과 양쪽 벽 생성
        static_lines = [
            [(0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT)],  # 바닥
            [(0, 0), (0, WINDOW_HEIGHT)],  # 왼쪽 벽
            [(WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT)]  # 오른쪽 벽
        ]

        for line in static_lines:
            shape = pymunk.Segment(self.space.static_body, line[0], line[1], 1)
            shape.friction = 0.5
            shape.elasticity = 0.5
            self.space.add(shape)

    def run(self):
        while True:
            if self.game_state.current_state == "MENU":
                self.run_menu()
            elif self.game_state.current_state == "GAME":
                self.run_game()
            elif self.game_state.current_state == "SCORES":
                self.run_scores()
            elif self.game_state.current_state == "GAME_OVER":
                self.run_game_over()

    def run_menu(self):
        while self.game_state.current_state == "MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.ui_manager.handle_menu_events(event, self.game_state)

            # 메뉴 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            self.ui_manager.draw_menu(self.score_manager.get_high_score())
            pygame.display.flip()
            self.clock.tick(60)

    def run_game(self):
        # 게임 상태 초기화
        self.game_state.reset()
        collision_handler = CollisionHandler(self.space, self.game_state)

        current_ball = None
        next_ball = GradeBall.create_random_grade(self.space, (WINDOW_WIDTH // 2, 100))

        last_drop_time = 0  # 마지막 공을 떨어뜨린 시간
        drop_delay = 1  # 공을 떨어뜨리는 최소 시간 간격 (초)

        while self.game_state.current_state == "GAME":
            to_remove = []  # 제거할 객체를 저장할 리스트
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    # 마우스 위치를 업데이트, 공이 떨어진 후에는 마우스 위치를 반영하지 않음
                    if not current_ball or current_ball.dropped:
                        self.mouse_pos = event.pos

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        current_time = pygame.time.get_ticks() / 1000  # 현재 시간 (초)

                        # if not current_ball or current_ball.dropped:  # 현재 공이 없거나 떨어진 경우
                        if (not current_ball or current_ball.dropped) and (current_time - last_drop_time >= drop_delay):
                            current_ball = next_ball
                            current_ball.drop()  # 공을 떨어뜨림
                            last_drop_time = current_time  # 현재 시간을 마지막 드롭 시간으로 설정

                            # 새로운 공을 생성할 때 마우스 X좌표 사용
                            next_ball = GradeBall.create_random_grade(self.space, (self.mouse_pos[0], 100))

            # 물리 엔진 업데이트
            self.space.step(1 / 60.0)

            # 게임 오버 체크
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    if shape.body.position.y < 100 and shape.grade_obj.dropped:
                        self.game_state.current_state = "GAME_OVER"
                        break

            # 제거할 객체 리스트 업데이트
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj') and shape.body.position.y < 100:
                    to_remove.append(shape)

            # 제거할 객체 한꺼번에 제거
            for shape in to_remove:
                self.space.remove(shape, shape.body)

            # 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            self.ui_manager.draw_game(self.game_state.score, self.game_state.round)

            # Game over line
            pygame.draw.line(self.screen, (255, 0, 0), (0, 100), (WINDOW_WIDTH, 100), 2)

            # 모든 객체 그리기
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    shape.grade_obj.draw(self.screen)
                elif hasattr(shape, 'item_obj'):
                    shape.item_obj.draw(self.screen)

            # 다음 공 미리 그리기
            # next_ball.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


    def check_collisions(self):
        """충돌한 공들을 확인하고 같은 등급이면 합치기"""
        # 같은 등급의 공들 체크
        balls_to_remove = []
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls[i + 1:], i + 1):
                if ball1.check_collision(ball2):
                    if ball1.grade == ball2.grade:
                        # 새로운 더 높은 등급의 공 생성
                        new_grade = ball1.get_next_grade()
                        if new_grade:
                            pos = ball1.get_position()
                            new_ball = GradeBall.create_specific_grade(self.space, pos, new_grade)
                            self.balls.append(new_ball)
                            self.score += GRADES[new_grade]['score']
                            balls_to_remove.extend([ball1, ball2])
                            break

        # 충돌한 공들 제거
        for ball in balls_to_remove:
            if ball in self.balls:
                self.balls.remove(ball)
                self.space.remove(ball.body, ball.shape)

    def check_game_over(self):
        """게임 오버 조건 체크"""
        game_over_line = 100
        for ball in self.balls:
            if ball.get_position()[1] <= game_over_line:
                return True
        return False

    def draw_game(self, score, next_ball):
        """게임 화면 그리기"""
        # 배경 그리기
        self.screen.fill(BACKGROUND_COLOR)

        # 게임 오버 라인 그리기
        pygame.draw.line(self.screen, (255, 0, 0), (0, 100), (WINDOW_WIDTH, 100), 2)

        # 점수 표시
        score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # 다음 공 미리보기
        if next_ball:
            next_ball.draw(self.screen)

        # 모든 공들 그리기
        for ball in self.balls:
            ball.draw(self.screen)


if __name__ == "__main__":
    game = GradeMerger()
    game.run()