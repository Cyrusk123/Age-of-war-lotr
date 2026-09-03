"""Procedural pygame presentation for the battlefield and interface."""

from __future__ import annotations

import math
import random

import pygame

from . import config as C
from .models import Unit


class Renderer:
    CARD_RECTS = [pygame.Rect(28 + i * 190, 610, 174, 88) for i in range(3)]

    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont("georgia", 46, bold=True)
        self.large_font = pygame.font.SysFont("georgia", 32, bold=True)
        self.medium_font = pygame.font.SysFont("segoeui", 21, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", 16)
        self.tiny_font = pygame.font.SysFont("segoeui", 13)
        self.background = self._make_background()
        self.particles: list[list[float]] = []
        self._rng = random.Random(4)

    def _make_background(self) -> pygame.Surface:
        surface = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        for y in range(C.SCREEN_HEIGHT):
            t = y / C.SCREEN_HEIGHT
            color = (int(24 + 32 * t), int(27 + 32 * t), int(34 + 23 * t))
            pygame.draw.line(surface, color, (0, y), (C.SCREEN_WIDTH, y))
        # Ashen mountains and distant Gondor hills.
        pygame.draw.polygon(surface, (38, 34, 38), [(0, 370), (120, 185), (230, 370)])
        pygame.draw.polygon(surface, (47, 39, 40), [(110, 370), (270, 235), (410, 370)])
        pygame.draw.polygon(surface, (44, 53, 54), [(650, 375), (810, 250), (930, 375)])
        pygame.draw.polygon(surface, (51, 65, 62), [(820, 375), (1040, 210), (1280, 375)])
        # Orodruin glow.
        pygame.draw.polygon(surface, (92, 43, 33), [(70, 350), (145, 195), (225, 350)])
        pygame.draw.polygon(surface, (221, 87, 35), [(139, 206), (150, 184), (159, 214)])
        # Ground split and central road.
        pygame.draw.rect(surface, (56, 49, 42), (0, 374, 640, 210))
        pygame.draw.rect(surface, (72, 88, 62), (640, 374, 640, 210))
        pygame.draw.polygon(surface, (106, 93, 72), [(0, 485), (1280, 470), (1280, 575), (0, 575)])
        pygame.draw.line(surface, (145, 125, 89), (0, 505), (1280, 490), 3)
        # Atmospheric silhouettes.
        rng = random.Random(8)
        for _ in range(65):
            x = rng.randrange(C.SCREEN_WIDTH)
            y = rng.randrange(80, 350)
            pygame.draw.circle(surface, (29, 30, 34), (x, y), rng.choice((1, 1, 2)))
        return surface

    def card_at(self, pos: tuple[int, int]) -> int | None:
        for index, rect in enumerate(self.CARD_RECTS):
            if rect.collidepoint(pos):
                return index
        return None

    def draw_game(self, screen: pygame.Surface, game, paused: bool = False,
                  show_help: bool = False) -> None:
        screen.blit(self.background, (0, 0))
        self._draw_bases(screen, game)
        for projectile in game.projectiles:
            self._draw_projectile(screen, projectile)
        for unit in sorted(game.units, key=lambda item: item.x):
            self._draw_unit(screen, unit, game.elapsed)
        self._update_and_draw_particles(screen, game)
        self._draw_hud(screen, game)
        if show_help:
            self._draw_help(screen)
        if paused:
            self._overlay(screen, "BATTLE PAUSED", "Press P or Esc to resume")
        elif game.state == "victory":
            self._overlay(screen, "VICTORY FOR MORDOR", "Gondor has fallen  •  Press R to march again")
        elif game.state == "defeat":
            self._overlay(screen, "MORDOR DEFEATED", "The Black Gate is lost  •  Press R to try again")

    def draw_title(self, screen: pygame.Surface, pulse: float) -> None:
        screen.blit(self.background, (0, 0))
        veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        veil.fill((4, 4, 6, 125))
        screen.blit(veil, (0, 0))
        self._draw_eye(screen, C.SCREEN_WIDTH // 2, 185, 1.35)
        self._center(screen, "WAR OF THE RING", self.title_font, (229, 181, 89), 285)
        self._center(screen, "MORDOR'S ASSAULT", self.large_font, (197, 67, 39), 344)
        self._center(screen, "Command Mordor. Break the armies of Gondor. Destroy their fortress.",
                     self.small_font, (214, 214, 202), 405)
        glow = int(180 + math.sin(pulse * 3) * 60)
        self._center(screen, "PRESS ENTER TO BEGIN", self.medium_font, (glow, glow, 150), 480)
        self._center(screen, "1–3 recruit units  •  Mouse selects cards  •  P pauses  •  F1 help",
                     self.small_font, (164, 169, 164), 535)
        self._center(screen, "A fan-made gameplay prototype with original procedural artwork",
                     self.tiny_font, (125, 128, 125), 674)

    def _draw_bases(self, screen: pygame.Surface, game) -> None:
        # Mordor fortress.
        pygame.draw.rect(screen, (33, 31, 29), (18, 335, 125, 215))
        pygame.draw.rect(screen, (48, 43, 39), (35, 290, 42, 260))
        pygame.draw.polygon(screen, (29, 27, 26), [(28, 300), (56, 247), (84, 300)])
        pygame.draw.rect(screen, (12, 12, 12), (75, 457, 61, 93))
        self._draw_eye(screen, 56, 330, 0.32)
        # Gondor citadel.
        pygame.draw.rect(screen, (177, 181, 174), (1139, 350, 123, 200))
        pygame.draw.rect(screen, (207, 207, 194), (1184, 295, 48, 255))
        pygame.draw.polygon(screen, (226, 223, 200), [(1176, 305), (1208, 260), (1240, 305)])
        pygame.draw.rect(screen, (72, 76, 74), (1144, 470, 54, 80))
        pygame.draw.circle(screen, (232, 232, 215), (1208, 346), 14, 3)
        self._bar(screen, pygame.Rect(24, 266, 120, 12), game.mordor.base_health / C.BASE_MAX_HEALTH,
                  (165, 47, 30))
        self._bar(screen, pygame.Rect(1136, 266, 120, 12), game.gondor.base_health / C.BASE_MAX_HEALTH,
                  (207, 210, 198))

    def _draw_eye(self, screen: pygame.Surface, x: int, y: int, scale: float) -> None:
        points = [(x - int(55 * scale), y), (x, y - int(25 * scale)),
                  (x + int(55 * scale), y), (x, y + int(25 * scale))]
        pygame.draw.polygon(screen, (191, 62, 30), points)
        pygame.draw.ellipse(screen, (246, 157, 37),
                            (x - 16 * scale, y - 25 * scale, 32 * scale, 50 * scale))
        pygame.draw.ellipse(screen, (20, 12, 8),
                            (x - 4 * scale, y - 23 * scale, 8 * scale, 46 * scale))

    def _draw_unit(self, screen: pygame.Surface, unit: Unit, time: float) -> None:
        x, y = int(unit.x), C.GROUND_Y
        bob = int(math.sin(time * 7 + unit.id) * 2)
        size = unit.kind.size
        mordor = unit.faction == "mordor"
        body = (83, 94, 65) if mordor else (201, 204, 201)
        accent = (151, 48, 30) if mordor else (52, 75, 101)
        if unit.flash_timer > 0:
            body = (255, 235, 210)
        pygame.draw.ellipse(screen, (30, 27, 24), (x - size, y + 17, size * 2, 8))
        # Legs and body.
        pygame.draw.line(screen, body, (x - 5, y + bob), (x - 7, y + 19), 5)
        pygame.draw.line(screen, body, (x + 5, y + bob), (x + 7, y + 19), 5)
        pygame.draw.polygon(screen, body, [(x - size // 2, y - 26 + bob),
                                            (x + size // 2, y - 26 + bob),
                                            (x + size // 2 + 3, y + 5 + bob),
                                            (x - size // 2 - 3, y + 5 + bob)])
        pygame.draw.rect(screen, accent, (x - size // 2 - 2, y - 10 + bob, size + 4, 7))
        pygame.draw.circle(screen, body, (x, y - 36 + bob), max(7, size // 2))
        if unit.kind.ranged:
            bow_x = x + unit.direction * 14
            pygame.draw.arc(screen, (126, 82, 43), (bow_x - 8, y - 40, 16, 35),
                            -math.pi / 2, math.pi / 2, 2)
            pygame.draw.line(screen, (193, 183, 154), (bow_x, y - 39), (bow_x, y - 6), 1)
        else:
            weapon_x = x + unit.direction * 15
            pygame.draw.line(screen, (181, 183, 174), (weapon_x, y - 33),
                             (weapon_x + unit.direction * 13, y - 12), 3)
        if unit.kind.key in ("uruk", "tower_guard"):
            pygame.draw.polygon(screen, accent, [(x - 12, y - 43 + bob), (x, y - 56 + bob),
                                                  (x + 12, y - 43 + bob)])
        self._bar(screen, pygame.Rect(x - 19, y - 65, 38, 5),
                  float(unit.health) / unit.kind.max_health,
                  (174, 50, 38) if mordor else (218, 220, 210), border=False)

    def _draw_projectile(self, screen: pygame.Surface, projectile) -> None:
        color = (236, 104, 36) if projectile.faction == "mordor" else (225, 225, 202)
        x = int(projectile.x)
        pygame.draw.line(screen, color, (x - 7, 450), (x + 7, 446), 3)

    def _draw_hud(self, screen: pygame.Surface, game) -> None:
        panel = pygame.Surface((C.SCREEN_WIDTH, 120), pygame.SRCALPHA)
        panel.fill((13, 14, 15, 235))
        screen.blit(panel, (0, 600))
        pygame.draw.line(screen, (123, 94, 50), (0, 600), (C.SCREEN_WIDTH, 600), 2)
        for i, (rect, kind) in enumerate(zip(self.CARD_RECTS, C.MORDOR_UNITS)):
            affordable, _ = game.can_recruit("mordor", kind.key)
            fill = (68, 50, 39) if affordable else (40, 40, 40)
            pygame.draw.rect(screen, fill, rect, border_radius=6)
            pygame.draw.rect(screen, (166, 119, 56) if affordable else (77, 77, 77), rect, 2, 6)
            self._text(screen, f"[{i + 1}] {kind.name}", self.small_font,
                       (235, 219, 185) if affordable else (125, 125, 125), rect.x + 10, rect.y + 9)
            self._text(screen, f"{kind.cost} gold", self.small_font, (226, 170, 67), rect.x + 10, rect.y + 37)
            role = "Ranged" if kind.ranged else ("Heavy" if kind.max_health > 200 else "Melee")
            self._text(screen, role, self.tiny_font, (167, 170, 165), rect.x + 10, rect.y + 62)
        self._text(screen, f"GOLD  {int(game.mordor.gold)}", self.medium_font, (233, 180, 62), 620, 620)
        self._text(screen, f"ARMY  {game.population('mordor')}/{C.POPULATION_CAP}",
                   self.medium_font, (207, 207, 193), 620, 652)
        queue = "  ›  ".join(f"{o.kind.name} {max(0, o.remaining):.1f}s" for o in game.mordor.queue)
        self._text(screen, "QUEUE  " + (queue or "Empty"), self.small_font, (168, 170, 163), 805, 623)
        minutes, seconds = divmod(int(game.elapsed), 60)
        self._text(screen, f"BATTLE {minutes:02}:{seconds:02}", self.small_font, (168, 170, 163), 1080, 655)
        if game.elapsed >= C.SIEGE_PRESSURE_START and game.state == "playing":
            self._text(screen, "SIEGE PRESSURE ACTIVE", self.tiny_font, (220, 99, 51), 1080, 680)
        if game.message_timer > 0:
            self._center(screen, game.message, self.small_font, (239, 202, 123), 574)

    def _update_and_draw_particles(self, screen: pygame.Surface, game) -> None:
        for event in game.events:
            if event.kind in ("hit", "base_hit", "death"):
                for _ in range(4 if event.kind != "death" else 10):
                    self.particles.append([event.x, 462.0, self._rng.uniform(-35, 35),
                                           self._rng.uniform(-70, -20), self._rng.uniform(.25, .65)])
        for particle in self.particles:
            particle[0] += particle[2] / C.FPS
            particle[1] += particle[3] / C.FPS
            particle[3] += 110 / C.FPS
            particle[4] -= 1 / C.FPS
            pygame.draw.circle(screen, (223, 94, 39), (int(particle[0]), int(particle[1])), 2)
        self.particles = [particle for particle in self.particles if particle[4] > 0]

    def _draw_help(self, screen: pygame.Surface) -> None:
        panel = pygame.Surface((600, 330), pygame.SRCALPHA)
        panel.fill((10, 11, 12, 242))
        screen.blit(panel, (340, 150))
        pygame.draw.rect(screen, (165, 121, 60), (340, 150, 600, 330), 2)
        self._center(screen, "COMMANDER'S GUIDE", self.large_font, (225, 181, 91), 176)
        lines = [
            "Destroy Gondor's fortress before the Black Gate falls.",
            "Gold arrives over time and is awarded for fallen enemies.",
            "Orc Warriors are cheap frontline troops.",
            "Orc Archers attack safely behind your line.",
            "Uruk-hai are slow, costly, and exceptionally durable.",
            "Controls: 1 / 2 / 3 recruit  •  P or Esc pause  •  F1 closes help",
        ]
        for i, line in enumerate(lines):
            self._center(screen, line, self.small_font, (207, 208, 198), 235 + i * 36)

    def _overlay(self, screen: pygame.Surface, title: str, subtitle: str) -> None:
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        screen.blit(shade, (0, 0))
        self._center(screen, title, self.title_font, (226, 171, 73), 290)
        self._center(screen, subtitle, self.medium_font, (218, 218, 205), 365)

    @staticmethod
    def _bar(screen, rect: pygame.Rect, ratio: float, color, border: bool = True) -> None:
        pygame.draw.rect(screen, (26, 25, 24), rect)
        inner = rect.inflate(-2, -2)
        inner.width = max(0, int(inner.width * max(0, min(1, ratio))))
        pygame.draw.rect(screen, color, inner)
        if border:
            pygame.draw.rect(screen, (16, 16, 16), rect, 2)

    @staticmethod
    def _text(screen, text, font, color, x, y) -> None:
        screen.blit(font.render(text, True, color), (x, y))

    @staticmethod
    def _center(screen, text, font, color, y) -> None:
        image = font.render(text, True, color)
        screen.blit(image, ((C.SCREEN_WIDTH - image.get_width()) // 2, y))