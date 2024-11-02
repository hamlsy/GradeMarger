# game_state.py
import sys

import grade as grade


class GameState:
    def __init__(self, screen=None):
        self.current_state = "MENU"  # MENU, GAME, SCORES, GAME_OVER
        self.score = 0
        self.round = 1
        self.screen = screen

    def reset(self):
        self.score = 0
        self.round = 1


# ui_manager.py
import pygame
import sys
from config import *


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.buttons = {}

    def create_button(self, text, pos, size):
        return pygame.Rect(pos[0], pos[1], size[0], size[1])

    def draw_menu(self, high_score):
        # 타이틀 그리기
        title = self.font.render("성적합치기", True, (0, 0, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 최고 점수 표시
        score_text = self.font.render(f"최고점수: {high_score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(score_text, score_rect)

        # 버튼 생성 및 그리기
        button_width, button_height = 200, 50
        start_button = self.create_button("게임 시작",
                                          (WINDOW_WIDTH // 2 - button_width // 2, 250),
                                          (button_width, button_height))
        scores_button = self.create_button("점수 기록",
                                           (WINDOW_WIDTH // 2 - button_width // 2, 320),
                                           (button_width, button_height))
        exit_button = self.create_button("게임 나가기",
                                         (WINDOW_WIDTH // 2 - button_width // 2, 390),
                                         (button_width, button_height))

        self.buttons = {
            "start": start_button,
            "scores": scores_button,
            "exit": exit_button
        }

        for text, button in self.buttons.items():
            pygame.draw.rect(self.screen, BUTTON_COLOR, button)
            button_text = self.font.render(text, True, BUTTON_TEXT_COLOR)
            text_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, text_rect)

    def draw_game(self, score, round_num):
        # 점수와 라운드 표시
        score_text = self.font.render(f"Score: {score}", True, (0, 0, 0))
        round_text = self.font.render(f"Round: {round_num}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(round_text, (10, 50))

        # 게임 오버 라인 표시
        pygame.draw.line(self.screen, (255, 0, 0), (0, 100), (WINDOW_WIDTH, 100), 2)

    def draw_game_over(self, score):
        # 게임 오버 화면
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {score}", True, (0, 0, 0))

        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)

        # 버튼 생성 및 그리기
        button_width, button_height = 200, 50
        retry_button = self.create_button("다시 시도",
                                          (WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT // 2 + 50),
                                          (button_width, button_height))
        menu_button = self.create_button("메인 메뉴",
                                         (WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT // 2 + 120),
                                         (button_width, button_height))

        self.buttons = {
            "retry": retry_button,
            "menu": menu_button
        }

        for text, button in self.buttons.items():
            pygame.draw.rect(self.screen, BUTTON_COLOR, button)
            button_text = self.font.render(text, True, BUTTON_TEXT_COLOR)
            text_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, text_rect)

    def draw_scores(self, scores):
        # 점수 기록 화면
        title = self.font.render("점수 기록", True, (0, 0, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # 점수 목록 표시
        y_offset = 120
        for i, (name, score) in enumerate(scores[:10], 1):  # 상위 10개만 표시
            score_text = self.font.render(f"{i}. {name}: {score}", True, (0, 0, 0))
            self.screen.blit(score_text, (WINDOW_WIDTH // 2 - 100, y_offset))
            y_offset += 40

        # 돌아가기 버튼
        button_width, button_height = 200, 50
        back_button = self.create_button("돌아가기",
                                         (WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT - 100),
                                         (button_width, button_height))

        self.buttons = {"back": back_button}

        pygame.draw.rect(self.screen, BUTTON_COLOR, back_button)
        button_text = self.font.render("돌아가기", True, BUTTON_TEXT_COLOR)
        text_rect = button_text.get_rect(center=back_button.center)
        self.screen.blit(button_text, text_rect)

    def handle_menu_events(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.buttons.get("start") and self.buttons["start"].collidepoint(mouse_pos):
                game_state.current_state = "GAME"
                game_state.reset()
            elif self.buttons.get("scores") and self.buttons["scores"].collidepoint(mouse_pos):
                game_state.current_state = "SCORES"
            elif self.buttons.get("exit") and self.buttons["exit"].collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()


# score_manager.py
import json
import os
from config import *


class ScoreManager:
    def __init__(self):
        self.scores_file = "scores.json"
        self.scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_scores(self):
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, name, score):
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)  # 높은 점수순으로 정렬
        self.save_scores()

    def get_high_score(self):
        if not self.scores:
            return 0
        return self.scores[0][1]

    def get_scores(self):
        return self.scores


# effects.py
import pygame
import random
from config import *


class Effects:
    @staticmethod
    def merge_effect(screen, pos, size):
        # 합치기 효과 - 파티클 생성
        particles = []
        for _ in range(10):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 5)
            particle = {
                'pos': list(pos),
                'vel': [speed * pygame.math.Vector2().from_polar((1, angle))[0],
                        speed * pygame.math.Vector2().from_polar((1, angle))[1]],
                'lifetime': 20
            }
            particles.append(particle)

        # 파티클 애니메이션
        for _ in range(20):
            for particle in particles:
                particle['pos'][0] += particle['vel'][0]
                particle['pos'][1] += particle['vel'][1]
                particle['lifetime'] -= 1

                if particle['lifetime'] > 0:
                    alpha = int(255 * (particle['lifetime'] / 20))
                    particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (*GRADES[grade]['color'], alpha), (2, 2), 2)
                    screen.blit(particle_surface, particle['pos'])

            pygame.display.flip()
            pygame.time.wait(20)