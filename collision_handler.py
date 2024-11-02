# collision_handler.py
import random
import sys

import pygame
import pymunk

from config import *
from game_objects import GradeBall, Item
from game_state import Effects


class CollisionHandler:
    def __init__(self, space, game_state):
        self.space = space
        self.game_state = game_state

        # 충돌 타입 설정
        # 1: 성적 공
        # 2: 아이템

        # 성적 공끼리의 충돌 핸들러 등록
        handler = space.add_collision_handler(1, 1)
        handler.separate = self.handle_grade_collision

        # 성적 공과 아이템의 충돌 핸들러 등록
        handler = space.add_collision_handler(1, 2)
        handler.separate = self.handle_item_collision

    def handle_grade_collision(self, arbiter, space, data):
        # 충돌한 두 공 가져오기
        ball_a = arbiter.shapes[0].grade_obj
        ball_b = arbiter.shapes[1].grade_obj

        # 같은 등급일 경우 합치기
        if ball_a.grade == ball_b.grade:
            pos_a = ball_a.body.position
            pos_b = ball_b.body.position

            # 새로운 위치 계산 (두 공의 중간)
            new_pos = ((pos_a.x + pos_b.x) / 2, (pos_a.y + pos_b.y) / 2)

            # 다음 등급 결정
            grade_order = ['F', 'D', 'C', 'B', 'A', 'A+']
            current_index = grade_order.index(ball_a.grade)

            if current_index < len(grade_order) - 1:
                # 새로운 등급의 공 생성
                new_grade = grade_order[current_index + 1]
                new_ball = GradeBall(space, new_pos, new_grade)

                # 점수 추가
                self.game_state.score += GRADES[new_grade]['score']

                # 효과 생성
                # Effects.merge_effect(space.screen, new_pos, GRADES[new_grade]['size'])
                # Effects.merge_effect(self.game_state.screen, new_pos, GRADES[new_grade]['size'])  # 수정된 부분

                # 이전 공들 제거
                space.remove(ball_a.shape, ball_a.body)
                space.remove(ball_b.shape, ball_b.body)

                # 새 공을 스페이스에 추가
                space.add(new_ball.body, new_ball.shape)

    def handle_item_collision(self, arbiter, space, data):
        # 아이템과 성적 공의 충돌 처리
        grade_ball = None
        item = None

        # 충돌한 객체 구분
        if hasattr(arbiter.shapes[0], 'grade_obj'):
            grade_ball = arbiter.shapes[0].grade_obj
            item = arbiter.shapes[1].item_obj
        else:
            grade_ball = arbiter.shapes[1].grade_obj
            item = arbiter.shapes[0].item_obj

        # 아이템 효과 적용
        if item.item_type == "과제":
            # 성적 한 단계 하락
            grade_order = ['F', 'D', 'C', 'B', 'A', 'A+']
            current_index = grade_order.index(grade_ball.grade)

            if current_index > 0:
                new_grade = grade_order[current_index - 1]
                new_ball = GradeBall(space, grade_ball.body.position, new_grade)
                space.remove(grade_ball.shape, grade_ball.body)

        elif item.item_type == "휴강":
            # 성적 한 단계 상승
            grade_order = ['F', 'D', 'C', 'B', 'A', 'A+']
            current_index = grade_order.index(grade_ball.grade)

            if current_index < len(grade_order) - 1:
                new_grade = grade_order[current_index + 1]
                new_ball = GradeBall(space, grade_ball.body.position, new_grade)
                space.remove(grade_ball.shape, grade_ball.body)

        # 아이템 제거
        space.remove(item.shape, item.body)

    # 메인 게임 루프 수정 (main.py의 run_game 메소드)
    def run_game(self):
        # 게임 상태 초기화
        self.game_state.reset()
        collision_handler = CollisionHandler(self.space, self.game_state)

        current_ball = None
        next_ball = GradeBall.create_random_grade(self.space, self.mouse_pos)

        # 게임 루프
        while self.game_state.current_state == "GAME":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                    if not current_ball or not current_ball.dropped:
                        next_ball.body.position = (event.pos[0], 100)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and (not current_ball or current_ball.dropped):
                        current_ball = next_ball
                        current_ball.drop()

                        # 새로운 공 생성
                        next_ball = GradeBall.create_random_grade(
                            self.space,
                            (self.mouse_pos[0], 100),
                            self.game_state.round
                        )

                        # 랜덤으로 아이템 생성
                        if random.random() < 0.1:  # 10% 확률로 아이템 생성
                            Item.create_random_item(self.space, (random.randint(50, WINDOW_WIDTH - 50), -20))

            # 물리 엔진 업데이트
            self.space.step(1 / 60.0)

            # 화면 그리기
            self.screen.fill(BACKGROUND_COLOR)
            self.ui_manager.draw_game(self.game_state.score, self.game_state.round)

            # 모든 객체 그리기
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    shape.grade_obj.draw(self.screen)
                elif hasattr(shape, 'item_obj'):
                    shape.item_obj.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

            # 게임 오버 체크
            game_over = False
            for shape in self.space.shapes:
                if hasattr(shape, 'grade_obj'):
                    if shape.body.position.y < 100 and shape.grade_obj.dropped:
                        game_over = True
                        break

            if game_over:
                self.game_state.current_state = "GAME_OVER"