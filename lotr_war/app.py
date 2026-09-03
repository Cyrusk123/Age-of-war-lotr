"""Pygame application, input handling, and screen state management."""

from __future__ import annotations

import pygame

from . import config as C
from .renderer import Renderer
from .simulation import GameSimulation


class GameApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("War of the Ring: Mordor's Assault")
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer()
        self.game = GameSimulation()
        self.screen_state = "title"
        self.paused = False
        self.show_help = False
        self.running = True

    def reset(self) -> None:
        self.game = GameSimulation()
        self.screen_state = "battle"
        self.paused = False
        self.show_help = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if self.screen_state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset()
                return
            if event.key == pygame.K_F1:
                self.show_help = not self.show_help
                return
            if event.key in (pygame.K_p, pygame.K_ESCAPE) and self.game.state == "playing":
                self.paused = not self.paused
                return
            if event.key == pygame.K_r and self.game.state != "playing":
                self.reset()
                return
            if self.screen_state == "battle" and not self.paused and not self.show_help:
                keys = {
                    pygame.K_1: "orc",
                    pygame.K_2: "orc_archer",
                    pygame.K_3: "uruk",
                    pygame.K_4: "warg_rider",
                    pygame.K_5: "olog_hai",
                    pygame.K_6: "lurtz",
                }
                if event.key in keys:
                    self.game.recruit("mordor", keys[event.key])
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.screen_state == "battle" and not self.paused and not self.show_help):
            index = self.renderer.card_at(event.pos)
            if index is not None:
                self.game.recruit("mordor", C.MORDOR_ROSTER[index].key)

    def run(self) -> int:
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            if self.screen_state == "title":
                self.renderer.draw_title(self.screen, pygame.time.get_ticks() / 1000)
            else:
                if not self.paused and not self.show_help:
                    self.game.update(dt)
                self.renderer.draw_game(self.screen, self.game, self.paused, self.show_help)
            pygame.display.flip()
        pygame.quit()
        return 0


def main() -> int:
    return GameApp().run()