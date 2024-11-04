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
#from game_state import Effects
from config import *


class GradeMerger:
    def __init__(self):
        # Pygame 초기화
        pygame.init()
        pygame.display.set_caption("성적합치기")

        # 한글 폰트 설정
        self.font = pygame.font.SysFont('malgun', FONT_SIZE)  # 맑은 고딕 폰트 사용

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

        # 게임 UI 관련 변수 추가
        self.guide_line_color = (200, 200, 200)  # 가이드 라인 색상
        self.next_ball = None

        self.game_over_countdown = None
        self.game_over_start_time = None
        self.show_exit_dialog = False
        self.GAME_OVER_LINE = 150



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

    def run_game_over(self):
        while self.game_state.current_state == "GAME_OVER":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.ui_manager.buttons.get("retry") and self.ui_manager.buttons["retry"].collidepoint(
                            mouse_pos):
                        self.game_state.current_state = "GAME"
                        self.game_state.reset()
                        return
                    elif self.ui_manager.buttons.get("exit") and self.ui_manager.buttons["exit"].collidepoint(
                            mouse_pos):
                        pygame.quit()
                        sys.exit()

            # 게임 오버 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            self.ui_manager.draw_game_over(self.game_state.score)
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        while True:
            if self.game_state.current_state == "MENU":
                self.run_menu()
            elif self.game_state.current_state == "GAME":
                self.run_game()
            elif self.game_state.current_state == "SCORES":
                self.run_scores()
            elif self.game_state.current_state == "TUTORIAL":  # 추가된 부분
                self.run_tutorial()
            elif self.game_state.current_state == "GAME_OVER":
                self.run_game_over()

    # main.py에 추가할 run_tutorial 메서드
    def run_tutorial(self):
        while self.game_state.current_state == "TUTORIAL":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 튜토리얼 창의 아무 곳이나 클릭하면 메뉴로 돌아감
                    self.game_state.current_state = "MENU"
                    return

            # 튜토리얼 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            tutorial_surface = self.ui_manager.create_tutorial_window()
            tutorial_rect = tutorial_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(tutorial_surface, tutorial_rect)
            pygame.display.flip()
            self.clock.tick(60)

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

        # 현재 공과 다음 공 초기화
        current_ball = None
        next_ball = GradeBall.create_random_grade(self.space, (WINDOW_WIDTH // 2, 100))

        self.mouse_pos = (WINDOW_WIDTH // 2, 0)
        last_drop_time = 0  # 마지막 공을 떨어뜨린 시간
        drop_delay = 1  # 공을 떨어뜨리는 최소 시간 간격 (초)

        # 게임 오버 관련 변수 초기화
        game_over_timer = None
        balls_above_line = set()  # 빨간 선 위에 있는 공들을 추적

        while self.game_state.current_state == "GAME":
            current_event = None

            collision_handler.process_merges()
            self.check_collisions()
            to_remove = []  # 제거할 객체를 저장할 리스트
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj') and hasattr(shape.grade_obj, 'to_remove'):
                    to_remove.append(shape)
                # 한 번에 제거
            for shape in to_remove:
                if shape in self.space.shapes:
                    self.space.remove(shape, shape.body)

            # 게임 오버 체크 로직
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    ball = shape.grade_obj
                    if ball.dropped and shape.body.position.y < self.GAME_OVER_LINE:
                        print("떨어진 상태면서 y가 GameOver보다 아래")
                        print("ball droped", ball.dropped)
                        print(shape.body.position.y)
                        ball_id = id(ball)
                        if ball_id not in balls_above_line:
                            balls_above_line.add(ball_id)
                            if game_over_timer is None:
                                game_over_timer = pygame.time.get_ticks()
                    else:
                        print("A")
                        print("ball droped", ball.dropped)
                        print(shape.body.position.y)
                        if id(ball) in balls_above_line:
                            balls_above_line.remove(id(ball))
                            if len(balls_above_line) == 0:
                                game_over_timer = None
                # 3초 타이머 체크
                if game_over_timer is not None:
                    if pygame.time.get_ticks() - game_over_timer >= 3000:  # 3초
                        self.game_state.current_state = "GAME_OVER"
                        return

                # processing 플래그 초기화
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    if hasattr(shape.grade_obj, 'processing'):
                        delattr(shape.grade_obj, 'processing')

            for event in pygame.event.get():
                current_event = event  # 현재 이벤트 저장
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show_exit_dialog = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    # 마우스 위치를 업데이트, 공이 떨어진 후에는 마우스 위치를 반영하지 않음

                    self.mouse_pos = (event.pos[0], 50)
                    if self.current_ball and not self.current_ball.dropped:
                        self.current_ball.body.position = self.mouse_pos


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
            self.check_collisions()


            # 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            # Next ball preview
            if next_ball:
                preview_pos = (WINDOW_WIDTH - 100, 50)
                next_ball.draw_preview(self.screen, preview_pos)
                preview_text = self.font.render("Next:", True, (0, 0, 0))
                self.screen.blit(preview_text, (WINDOW_WIDTH - 150, 40))

            # 카운트다운 표시
            self.draw_countdown()

            # UI 그리기
            self.ui_manager.draw_game(self.game_state.score, self.game_state.round)

            # Game over line
            pygame.draw.line(self.screen, (255, 0, 0), (0, 100), (WINDOW_WIDTH, 100), 2)

            # 가이드 라인 그리기
            pygame.draw.line(
                self.screen,
                self.guide_line_color,
                (self.mouse_pos[0], 100),  # 시작점 (게임오버 라인)
                (self.mouse_pos[0], WINDOW_HEIGHT),  # 끝점
                2
            )

            # 종료 대화상자 표시 -> esc로직
            if self.show_exit_dialog:
                dialog_rect, exit_button, cancel_button = self.draw_exit_dialog()

                # 마우스 클릭 처리
                mouse_pos = pygame.mouse.get_pos()
                # 현재 이벤트가 있고 마우스 클릭인 경우에만 처리
                if current_event and current_event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if exit_button.collidepoint(mouse_pos):
                        self.game_state.reset()  # 게임 상태 초기화
                        self.game_state.current_state = "MENU"
                        self.show_exit_dialog = False  # ESC 창 닫기
                        return
                    elif cancel_button.collidepoint(mouse_pos):
                        self.show_exit_dialog = False


            # 모든 객체 그리기
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    shape.grade_obj.draw(self.screen)
                elif hasattr(shape, 'item_obj'):
                    shape.item_obj.draw(self.screen)

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

    def draw_exit_dialog(self):
        """ESC 눌렀을 때 나타나는 종료 대화상자 그리기"""
        dialog_surface = pygame.Surface((300, 150))
        dialog_surface.fill((255, 255, 255))

        # 대화상자 테두리
        pygame.draw.rect(dialog_surface, (0, 0, 0), (0, 0, 300, 150), 2)

        # 텍스트 렌더링
        font = pygame.font.SysFont('malgun', 24)
        text = font.render("게임을 나가시겠습니까?", True, (0, 0, 0))
        text_rect = text.get_rect(center=(150, 40))
        dialog_surface.blit(text, text_rect)

        # 버튼 생성
        exit_button = pygame.Rect(50, 80, 100, 40)
        cancel_button = pygame.Rect(150, 80, 100, 40)

        # 버튼 그리기
        pygame.draw.rect(dialog_surface, (200, 0, 0), exit_button)
        pygame.draw.rect(dialog_surface, (100, 100, 100), cancel_button)

        # 버튼 텍스트
        exit_text = font.render("Exit", True, (255, 255, 255))
        cancel_text = font.render("Cancel", True, (255, 255, 255))

        dialog_surface.blit(exit_text, exit_text.get_rect(center=exit_button.center))
        dialog_surface.blit(cancel_text, cancel_text.get_rect(center=cancel_button.center))

        # 화면 중앙에 대화상자 표시
        dialog_rect = dialog_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(dialog_surface, dialog_rect)

        return dialog_rect, exit_button.move(dialog_rect.x, dialog_rect.y), \
               cancel_button.move(dialog_rect.x, dialog_rect.y)

    def draw_countdown(self):
        """게임오버 카운트다운 표시"""
        if self.game_over_countdown is not None:
            remaining_time = max(0, 3 - (pygame.time.get_ticks() - self.game_over_start_time) / 1000)
            if remaining_time > 0:
                font = pygame.font.SysFont('malgun', 72)
                text = font.render(f"{int(remaining_time) + 1}", True, (255, 0, 0))
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(text, text_rect)
            else:
                self.game_state.current_state = "GAME_OVER"
                self.game_over_countdown = None

    def create_next_object(self, space, pos):
        """다음 오브젝트 생성 (공 또는 아이템)"""
        if random.random() < 0.5:  # 20% 확률로 아이템 생성
            item_types = ["과제", "휴강"]
            return Item(space, pos, random.choice(item_types))
        else:
            return GradeBall.create_random_grade(space, pos)


if __name__ == "__main__":
    game = GradeMerger()
    game.run()