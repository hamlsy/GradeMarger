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
        self.show_tutorial = False

        # 배경 이미지 로드 (배경 이미지가 있다고 가정)
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill((240, 248, 255))  # 연한 하늘색 배경
        # 패턴 추가
        for i in range(0, WINDOW_WIDTH, 30):
            for j in range(0, WINDOW_HEIGHT, 30):
                if (i + j) % 60 == 0:
                    pygame.draw.circle(self.background, (230, 240, 250), (i, j), 5)

    def create_tutorial_window(self):
        tutorial_surface = pygame.Surface((600, 400))
        # 그라데이션 배경
        for i in range(400):
            color = (255 - i // 4, 255 - i // 4, 255)
            pygame.draw.line(tutorial_surface, color, (0, i), (600, i))

        # 테두리 추가
        tutorial_surface.fill((255, 255, 255))

        tutorial_text = [
            ("How to Play", 36, (0, 0, 0)),
            "",
            ("1. Drop balls by clicking SPACE", 24, (50, 50, 50)),
            ("   - Merge same grades to get higher grades", 20, (70, 70, 70)),
            "",
            ("2. Items can appear randomly:", 24, (50, 50, 50)),
            ("   - Assignment: Decreases grade", 20, (70, 70, 70)),
            ("   - Class Canceled: Increases grade", 20, (70, 70, 70)),
            "",
            ("3. Game Over Conditions:", 24, (50, 50, 50)),
            ("   - Balls stay above red line for 3 seconds", 20, (70, 70, 70)),
            "",
            ("Tips:", 24, (50, 50, 50)),
            ("- Plan your drops carefully", 20, (70, 70, 70)),
            ("- Watch out for the red line!", 20, (70, 70, 70))
        ]

        y = 20
        for line in tutorial_text:
            if isinstance(line, tuple):
                text, size, color = line
                font = pygame.font.SysFont(None, size)
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(x=20, y=y)
                tutorial_surface.blit(text_surface, text_rect)
                y += size + 5
            else:
                y += 20

        return tutorial_surface

    def create_button(self, text, pos, size):
        return pygame.Rect(pos[0], pos[1], size[0], size[1])

    def draw_menu(self, high_score):
        # 배경 그리기
        self.screen.blit(self.background, (0, 0))

        # 게임 방법 창 표시
        if self.show_tutorial:
            tutorial_surface = self.create_tutorial_window()
            tutorial_rect = tutorial_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(tutorial_surface, tutorial_rect)

        # 타이틀 그리기
        title = self.font.render("Grade Merger!", True, (0, 0, 0))
        # 타이틀 효과
        title = "Grade Merger!"
        font_size = 72
        font = pygame.font.SysFont(None, font_size)

        # 그림자 효과
        shadow = font.render(title, True, (100, 100, 100))
        shadow_rect = shadow.get_rect(center=(WINDOW_WIDTH // 2 + 3, 103))
        self.screen.blit(shadow, shadow_rect)

        # 메인 텍스트
        text = font.render(title, True, (0, 0, 150))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(text, text_rect)

        # 최고 점수 표시 (장식된 프레임 안에)
        score_frame = pygame.Surface((300, 60))
        score_frame.fill((240, 240, 255))
        pygame.draw.rect(score_frame, (100, 100, 200), (0, 0, 300, 60), 3)
        score_text = self.font.render(f"High Score: {high_score}", True, (0, 0, 100))
        score_rect = score_text.get_rect(center=(150, 30))
        score_frame.blit(score_text, score_rect)
        self.screen.blit(score_frame, (WINDOW_WIDTH // 2 - 150, 150))

        # 버튼 디자인 개선
        button_colors = {
            "start": ((50, 150, 50), (70, 170, 70)),
            "how to play": ((50, 50, 150), (70, 70, 170)),
            "exit": ((150, 50, 50), (170, 70, 70))
        }
        button_width, button_height = 200, 50
        y_positions = {"start": 250, "how to play": 350, "exit": 450}

        # 버튼 생성 및 그리기
        button_width, button_height = 200, 50
        start_button = self.create_button("게임 시작",
                                          (WINDOW_WIDTH // 2 - button_width // 2, 250),
                                          (button_width, button_height))

        # 기존 메뉴 버튼에 게임 방법 버튼 추가
        tutorial_button = self.create_button("게임 방법",
                                             (WINDOW_WIDTH // 2 - button_width // 2, 350),
                                             (button_width, button_height))
        self.buttons["tutorial"] = tutorial_button

        #scores_button = self.create_button("점수 기록",
        #                                   (WINDOW_WIDTH // 2 - button_width // 2, 450),
        #                                   (button_width, button_height))
        exit_button = self.create_button("게임 나가기",
                                         (WINDOW_WIDTH // 2 - button_width // 2, 450),
                                         (button_width, button_height))

        self.buttons = {
            "start": start_button,
            "how to play": tutorial_button,
            #"scores": scores_button,
            "exit": exit_button
        }

        for text, y_pos in y_positions.items():
            button = self.create_button(text,
                                        (WINDOW_WIDTH // 2 - button_width // 2, y_pos),
                                        (button_width, button_height))
            self.buttons[text] = button

            # 버튼 그리기 (그라데이션 효과)
            base_color, hover_color = button_colors[text]
            mouse_pos = pygame.mouse.get_pos()
            color = hover_color if button.collidepoint(mouse_pos) else base_color

            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, (255, 255, 255), button, 2)

            button_text = self.font.render(text.title(), True, (255, 255, 255))
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

        # Try Again과 Exit 버튼 추가
        button_width, button_height = 200, 50
        retry_button = self.create_button("Try Again",
                                          (WINDOW_WIDTH // 2 - button_width - 10, WINDOW_HEIGHT // 2 + 50),
                                          (button_width, button_height))
        exit_button = self.create_button("Exit",
                                         (WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 + 50),
                                         (button_width, button_height))

        self.buttons = {
            "retry": retry_button,
            "exit": exit_button
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

            elif self.buttons.get("how to play") and self.buttons["how to play"].collidepoint(mouse_pos):
                game_state.current_state = "TUTORIAL"

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
