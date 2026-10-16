import math
import random
import pygame


class GameEngine:

    # AI phases
    PHASE_NORMAL = "NORMAL"
    PHASE_SURGE = "SURGE"
    PHASE_COOLDOWN = "COOLDOWN"

    # Tunables (durations are in frames; the game runs at 60 FPS)
    NORMAL_FRAMES = 180          # ~3.0s of steady pressure
    SURGE_FRAMES = 90            # ~1.5s of high power
    COOLDOWN_FRAMES = 150        # ~2.5s of reduced resistance
    SURGE_MULTIPLIER = 3.0
    COOLDOWN_MULTIPLIER = 0.3

    COUNTER_WINDOW_FRAMES = 60   # first ~1.0s of cooldown is the "perfect timing" window
    COUNTER_DURATION_FRAMES = 180  # ~3.0s of boosted comeback
    COUNTER_PUSH_MULTIPLIER = 2.0
    COUNTER_STAMINA_BURST = 40.0   # instant stamina refund on a successful counter
    COUNTER_EXTRA_REGEN = 1.5      # extra stamina regen per frame while counter is active

    BASE_PUSH = 4.2
    EXHAUST_THRESHOLD = 30

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None

        self.stamina = 100.0
        self.max_stamina = 100.0

        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35

        # AI surge cycle (Task 2)
        self.ai_phase = self.PHASE_NORMAL
        self.phase_timer = self.NORMAL_FRAMES
        self.phase_elapsed = 0

        # Counter-surge (Task 4)
        self.counter_timer = 0
        self.counter_used_this_cooldown = False
        self.counter_flash_timer = 0  # short "COUNTER!" flash after triggering

        self.frame_count = 0

        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    # Helpers

    def is_exhausted(self):
        return self.stamina <= self.EXHAUST_THRESHOLD

    def in_counter_window(self):
        return (
            self.ai_phase == self.PHASE_COOLDOWN
            and self.phase_elapsed <= self.COUNTER_WINDOW_FRAMES
            and not self.counter_used_this_cooldown
        )

    def counter_active(self):
        return self.counter_timer > 0

    def _set_phase(self, phase):
        self.ai_phase = phase
        self.phase_elapsed = 0
        if phase == self.PHASE_NORMAL:
            self.phase_timer = self.NORMAL_FRAMES
        elif phase == self.PHASE_SURGE:
            self.phase_timer = self.SURGE_FRAMES
        else:
            self.phase_timer = self.COOLDOWN_FRAMES
            self.counter_used_this_cooldown = False

    def _ai_multiplier(self):
        if self.ai_phase == self.PHASE_SURGE:
            return self.SURGE_MULTIPLIER
        if self.ai_phase == self.PHASE_COOLDOWN:
            return self.COOLDOWN_MULTIPLIER
        return 1.0

    # Input

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if event.key not in (pygame.K_LEFT, pygame.K_RIGHT):
                return

            if self.is_exhausted():
                return

            # Must alternate keys
            if self.last_key == event.key:
                return

            # Task 4: pushing right as the AI's surge ends triggers the counter-surge
            if self.in_counter_window():
                self.counter_timer = self.COUNTER_DURATION_FRAMES
                self.counter_used_this_cooldown = True
                self.counter_flash_timer = 60
                self.stamina = min(self.max_stamina, self.stamina + self.COUNTER_STAMINA_BURST)

            push = self.BASE_PUSH
            if self.counter_active():
                push *= self.COUNTER_PUSH_MULTIPLIER

            # Task 1 fix: player input pulls the arm toward the player's side (negative)
            self.arm_position -= push
            self.stamina = max(0.0, self.stamina - 2.0)
            self.last_key = event.key

    # Update

    def update(self):
        if self.game_state != "PLAYING":
            return

        self.frame_count += 1

        # Task 2: advance AI phase cycle NORMAL -> SURGE -> COOLDOWN -> NORMAL
        self.phase_timer -= 1
        self.phase_elapsed += 1
        if self.phase_timer <= 0:
            if self.ai_phase == self.PHASE_NORMAL:
                self._set_phase(self.PHASE_SURGE)
            elif self.ai_phase == self.PHASE_SURGE:
                self._set_phase(self.PHASE_COOLDOWN)
            else:
                self._set_phase(self.PHASE_NORMAL)

        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += self.ai_strength * ai_variance * self._ai_multiplier()

        # Stamina regen (+ bonus during counter-surge)
        regen = 0.15
        if self.counter_active():
            regen += self.COUNTER_EXTRA_REGEN
        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + regen)

        if self.counter_timer > 0:
            self.counter_timer -= 1
        if self.counter_flash_timer > 0:
            self.counter_flash_timer -= 1

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.ai_phase = self.PHASE_NORMAL
        self.phase_timer = self.NORMAL_FRAMES
        self.phase_elapsed = 0
        self.counter_timer = 0
        self.counter_used_this_cooldown = False
        self.counter_flash_timer = 0
        self.frame_count = 0

    # Render

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        # ---- Stamina bar ----
        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        if self.counter_active():
            bar_color = (80, 220, 255)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)

        # ---- AI phase bar (shows where the AI is in its cycle) ----
        ai_label = self.font_med.render("AI POWER", True, (220, 220, 220))
        screen.blit(ai_label, (40, 485))
        ai_bg = pygame.Rect(140, 488, 240, 22)
        pygame.draw.rect(screen, (45, 50, 60), ai_bg, border_radius=6)
        if self.ai_phase == self.PHASE_SURGE:
            ai_color, ai_fill_w = (240, 70, 50), 240
        elif self.ai_phase == self.PHASE_COOLDOWN:
            ai_color, ai_fill_w = (90, 140, 230), 240 * 0.2
        else:
            ai_color, ai_fill_w = (230, 170, 60), 240 * 0.5
        pygame.draw.rect(
            screen, ai_color, pygame.Rect(140, 488, int(ai_fill_w), 22), border_radius=6
        )
        phase_text = self.font_med.render(self.ai_phase, True, ai_color)
        screen.blit(phase_text, (395, 488))

        # ---- Task 3: warning indicators ----
        flash_on = (self.frame_count // 8) % 2 == 0
        indicator_y = 530

        if self.ai_phase == self.PHASE_SURGE and flash_on:
            warn = self.font_big.render("!! AI SURGE !!", True, (255, 80, 60))
            screen.blit(warn, (self.width // 2 - warn.get_width() // 2, indicator_y))
            indicator_y += 38
        elif self.ai_phase == self.PHASE_SURGE:
            indicator_y += 38

        if self.is_exhausted() and self.game_state == "PLAYING":
            exh = self.font_big.render("EXHAUSTED!", True, (255, 200, 40))
            screen.blit(exh, (self.width // 2 - exh.get_width() // 2, indicator_y))
            indicator_y += 38

        # ---- Task 4: counter-surge prompts ----
        if self.in_counter_window() and flash_on:
            prompt = self.font_big.render("COUNTER NOW! PUSH!", True, (80, 230, 255))
            screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, 530))
        elif self.counter_active():
            secs = self.counter_timer / 60.0
            txt = self.font_med.render(
                f"COUNTER-SURGE ACTIVE  x2 PUSH  ({secs:.1f}s)", True, (80, 230, 255)
            )
            screen.blit(txt, (self.width // 2 - txt.get_width() // 2, 585))

        # ---- Game over overlay ----
        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
