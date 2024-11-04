# collision_handler.py
import random
import sys

import pygame
import pymunk

from config import *
from game_objects import GradeBall, Item
#from game_state import Effects


class CollisionHandler:
    def __init__(self, space, game_state):
        self.space = space
        self.game_state = game_state
        self.merge_queue = []
        self.call_back_key = 0
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

        # 이미 제거 예정이거나 처리 중인 공은 무시
        if (hasattr(ball_a, 'to_remove') or hasattr(ball_b, 'to_remove') or
                hasattr(ball_a, 'processing') or hasattr(ball_b, 'processing')):
            return

        # 같은 등급일 경우 합치기 큐에 추가
        if ball_a.grade == ball_b.grade:
            self.merge_queue.append((ball_a, ball_b))
            # 처리 중 표시
            ball_a.processing = True
            ball_b.processing = True


    def process_merges(self):
        """합치기 큐에 있는 모든 공을 처리"""
        if not self.merge_queue:
            return

        # 현재 프레임의 모든 병합 작업 처리
        while self.merge_queue:
            ball_a, ball_b = self.merge_queue.pop(0)

            # 이미 제거된 공은 건너뛰기 v1
            if hasattr(ball_a, 'to_remove') or hasattr(ball_b, 'to_remove'):
                continue

            # 새로운 위치 계산
            pos_a = ball_a.body.position
            pos_b = ball_b.body.position
            new_pos = ((pos_a.x + pos_b.x) / 2, (pos_a.y + pos_b.y) / 2)

            # 다음 등급 결정
            grade_order = ['F', 'D', 'C', 'B', 'A', 'A+']
            current_index = grade_order.index(ball_a.grade)

            if current_index < len(grade_order) - 1:
                # 새 공 생성
                new_grade = grade_order[current_index + 1]
                new_ball = GradeBall(self.space, new_pos, new_grade)

                # 점수 추가
                self.game_state.score += GRADES[new_grade]['score']

                # 이전 공들 제거 표시
                ball_a.to_remove = True
                ball_b.to_remove = True

                # 새 공 추가 및 주변 공들과의 즉시 충돌 체크
                def add_new_ball():
                    # 이전 공들 제거
                    if ball_a in self.space.shapes:
                        self.space.remove(ball_a.shape, ball_a.body)
                    if ball_b in self.space.shapes:
                        self.space.remove(ball_b.shape, ball_b.body)

                    # 새 공 추가
                    self.space.add(new_ball.body, new_ball.shape)

                    # 주변 공들과의 충돌 즉시 체크
                    for shape in self.space.shapes:
                        if (hasattr(shape, 'grade_obj') and
                            shape.grade_obj != new_ball and
                            shape.grade_obj.grade == new_ball.grade):
                            # 거리 체크
                            dist = ((shape.body.position.x - new_ball.body.position.x) ** 2 +
                                    (shape.body.position.y - new_ball.body.position.y) ** 2) ** 0.5
                            if dist < (shape.radius + new_ball.shape.radius) * 1.5:  # 약간의 여유를 둠
                                self.merge_queue.append((shape.grade_obj, new_ball))

                    # 고유한 키를 사용하여 콜백 등록
                    self.callback_key += 1
                    self.space.add_post_step_callback(add_new_ball, self.callback_key)

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

