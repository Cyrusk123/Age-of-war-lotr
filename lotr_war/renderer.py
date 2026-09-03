"""Layered procedural artwork and interface for the battlefield."""

from __future__ import annotations

import math
import random

import pygame

from . import config as C
from .models import Unit


class Renderer:
    CARD_RECTS = [pygame.Rect(14 + i * 148, 610, 140, 88) for i in range(6)]

    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont("constantia,georgia", 46, bold=True)
        self.large_font = pygame.font.SysFont("constantia,georgia", 32, bold=True)
        self.medium_font = pygame.font.SysFont("cambria,georgia", 20, bold=True)
        self.small_font = pygame.font.SysFont("candara,segoeui", 16)
        self.tiny_font = pygame.font.SysFont("candara,segoeui", 13)
        self.background = self._make_background()
        self.particles: list[list[float]] = []
        self._rng = random.Random(4)

    def _make_background(self) -> pygame.Surface:
        surface = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        # Storm sky shifts from volcanic brown to cold Gondor blue.
        for y in range(C.SCREEN_HEIGHT):
            t = y / C.SCREEN_HEIGHT
            left = (int(13 + 37 * t), int(16 + 29 * t), int(22 + 20 * t))
            right = (int(17 + 40 * t), int(22 + 48 * t), int(30 + 42 * t))
            for x in range(0, C.SCREEN_WIDTH, 16):
                side = x / C.SCREEN_WIDTH
                color = tuple(int(left[i] * (1 - side) + right[i] * side) for i in range(3))
                pygame.draw.rect(surface, color, (x, y, 16, 1))
        # Far ranges, haze, and snow cuts create atmospheric depth.
        pygame.draw.polygon(surface, (30, 30, 35), [(0, 374), (88, 278), (157, 338),
                            (271, 218), (387, 354), (514, 254), (650, 374)])
        pygame.draw.polygon(surface, (42, 51, 54), [(526, 374), (677, 276), (752, 328),
                            (855, 226), (943, 318), (1061, 179), (1280, 360), (1280, 390)])
        pygame.draw.polygon(surface, (58, 67, 65), [(757, 374), (887, 288), (947, 331),
                            (1061, 212), (1130, 279), (1206, 222), (1280, 285), (1280, 390)])
        pygame.draw.polygon(surface, (128, 133, 127), [(1061, 212), (1037, 245),
                            (1062, 236), (1081, 254)])
        pygame.draw.polygon(surface, (116, 122, 118), [(1206, 222), (1189, 245),
                            (1208, 239), (1223, 252)])
        # Volcano, lava scar, and layered smoke.
        pygame.draw.polygon(surface, (53, 28, 27), [(0, 374), (88, 321), (144, 176),
                            (180, 268), (253, 374)])
        pygame.draw.polygon(surface, (101, 39, 27), [(89, 321), (144, 176), (155, 230), (132, 212)])
        pygame.draw.polygon(surface, (233, 79, 25), [(136, 191), (144, 176), (151, 203), (143, 221)])
        pygame.draw.ellipse(surface, (46, 35, 36), (103, 130, 89, 48))
        pygame.draw.ellipse(surface, (35, 31, 35), (120, 91, 126, 55))
        pygame.draw.ellipse(surface, (28, 29, 34), (167, 57, 155, 65))
        # Midground ridges, forests, and tiny ruins establish scale.
        pygame.draw.polygon(surface, (49, 42, 36), [(0, 385), (112, 344), (205, 370),
                            (320, 328), (436, 378), (548, 343), (650, 385)])
        pygame.draw.polygon(surface, (54, 70, 55), [(590, 386), (715, 332), (825, 366),
                            (937, 308), (1042, 352), (1155, 301), (1280, 340), (1280, 395)])
        for x in range(674, 1270, 33):
            h = 8 + (x * 7) % 13
            pygame.draw.polygon(surface, (36, 51, 42), [(x - 7, 382), (x, 382 - h), (x + 7, 382)])
        # Ground split and churned central road.
        pygame.draw.rect(surface, (56, 49, 42), (0, 374, 640, 210))
        pygame.draw.rect(surface, (72, 88, 62), (640, 374, 640, 210))
        pygame.draw.polygon(surface, (104, 87, 63), [(0, 473), (180, 469), (355, 479),
                            (533, 467), (725, 474), (918, 462), (1090, 469), (1280, 455),
                            (1280, 574), (0, 574)])
        pygame.draw.polygon(surface, (80, 67, 50), [(0, 514), (211, 504), (420, 515),
                            (638, 503), (851, 508), (1062, 494), (1280, 500),
                            (1280, 563), (0, 563)])
        pygame.draw.lines(surface, (139, 117, 79), False, [(0, 490), (205, 485),
                          (436, 495), (680, 484), (936, 489), (1280, 474)], 2)
        rng = random.Random(17)
        for _ in range(210):
            x, y = rng.randrange(1280), rng.randrange(390, 574)
            colors = ((67, 55, 43), (43, 39, 35), (82, 63, 43)) if x < 640 else (
                (73, 87, 59), (54, 68, 50), (95, 91, 62))
            color = rng.choice(colors)
            pygame.draw.line(surface, color, (x, y), (x + rng.randrange(2, 8), y - rng.randrange(0, 3)))
        for x in (185, 338, 594, 703, 984, 1088):
            pygame.draw.line(surface, (48, 39, 31), (x, 494), (x + 12, 474), 3)
            pygame.draw.line(surface, (48, 39, 31), (x + 5, 481), (x + 16, 492), 2)
        pygame.draw.rect(surface, (22, 23, 23), (0, 584, 1280, 16))
        return surface.convert()

    def card_at(self, pos: tuple[int, int]) -> int | None:
        for index, rect in enumerate(self.CARD_RECTS):
            if rect.collidepoint(pos):
                return index
        return None

    def draw_game(self, screen: pygame.Surface, game, paused: bool = False,
                  show_help: bool = False) -> None:
        screen.blit(self.background, (0, 0))
        self._draw_ambient(screen, game.elapsed)
        self._draw_bases(screen, game)
        for projectile in game.projectiles:
            self._draw_projectile(screen, projectile)
        for unit in sorted(game.units, key=lambda item: item.x):
            self._draw_unit(screen, unit, game.elapsed)
        self._update_and_draw_particles(screen, game)
        self._draw_foreground(screen, game.elapsed)
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
        self._draw_ambient(screen, pulse * .4)
        veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        veil.fill((4, 4, 6, 125))
        screen.blit(veil, (0, 0))
        pygame.draw.line(screen, (121, 84, 39), (390, 270), (890, 270), 1)
        pygame.draw.line(screen, (72, 58, 39), (435, 394), (845, 394), 1)
        self._draw_eye(screen, C.SCREEN_WIDTH // 2, 178, 1.25)
        self._center_shadow(screen, "WAR OF THE RING", self.title_font, (232, 186, 91), 280)
        self._center_shadow(screen, "MORDOR'S ASSAULT", self.large_font, (202, 70, 36), 337)
        self._center(screen, "Command the dark host. Break the white walls. Claim the realm.",
                     self.small_font, (207, 207, 191), 403)
        glow = int(180 + math.sin(pulse * 3) * 60)
        button = pygame.Rect(476, 461, 328, 54)
        pygame.draw.rect(screen, (28, 24, 20), button, border_radius=3)
        pygame.draw.rect(screen, (128, 88, 38), button, 2, border_radius=3)
        self._center(screen, "PRESS ENTER TO BEGIN", self.medium_font, (glow, glow, 150), 476)
        self._center(screen, "1-6 recruit  |  Mouse selects  |  P pauses  |  F1 guide",
                     self.small_font, (157, 161, 153), 543)
        self._center(screen, "An original fan-made procedural battle",
                     self.tiny_font, (109, 114, 109), 676)

    @staticmethod
    def _draw_ambient(screen: pygame.Surface, elapsed: float) -> None:
        """Draw deterministic moving haze, ash, and embers."""
        haze = pygame.Surface((1280, 390), pygame.SRCALPHA)
        for i in range(7):
            x = int((i * 231 + elapsed * (4 + i % 3)) % 1480) - 130
            y = 65 + (i * 43) % 190
            pygame.draw.ellipse(haze, (18, 20, 24, 25), (x, y, 190 + i * 11, 28 + i * 3))
        screen.blit(haze, (0, 0))
        for i in range(34):
            x = int((i * 79 + elapsed * (12 + i % 5)) % 670)
            y = int((i * 113 + elapsed * (5 + i % 4)) % 430) + 45
            color = (174, 82, 36) if i % 4 == 0 else (75, 70, 66)
            pygame.draw.circle(screen, color, (x, y), 2 if i % 5 == 0 else 1)

    @staticmethod
    def _draw_foreground(screen: pygame.Surface, elapsed: float) -> None:
        pygame.draw.polygon(screen, (28, 28, 25), [(0, 584), (0, 570), (78, 579),
                            (161, 568), (260, 582), (358, 575), (470, 584)])
        pygame.draw.polygon(screen, (35, 42, 33), [(808, 584), (906, 577), (1010, 581),
                            (1118, 570), (1280, 579), (1280, 600), (808, 600)])
        for x in (23, 72, 116, 1042, 1094, 1160, 1232):
            sway = int(math.sin(elapsed * 1.4 + x) * 2)
            pygame.draw.line(screen, (52, 60, 43), (x, 588), (x + sway, 570 - x % 11), 2)

    def _draw_bases(self, screen: pygame.Surface, game) -> None:
        mordor_health = game.mordor.base_health / C.BASE_MAX_HEALTH
        gondor_health = game.gondor.base_health / C.BASE_MAX_HEALTH
        # Jagged basalt gate: layered walls, towers, spikes, masonry, and banner.
        pygame.draw.rect(screen, (42, 37, 33), (18, 350, 125, 200))
        pygame.draw.polygon(screen, (55, 46, 38), [(18, 350), (42, 329), (71, 350),
                            (100, 323), (143, 350)])
        pygame.draw.rect(screen, (35, 31, 29), (31, 298, 43, 158))
        pygame.draw.polygon(screen, (25, 23, 22), [(23, 304), (39, 267), (53, 297),
                            (65, 259), (82, 304)])
        for y in range(370, 535, 22):
            pygame.draw.line(screen, (65, 55, 47), (22, y), (140, y), 1)
        pygame.draw.rect(screen, (9, 10, 10), (66, 447, 61, 103))
        pygame.draw.polygon(screen, (9, 10, 10), [(66, 447), (96, 411), (127, 447)])
        for x in (28, 48, 69, 116, 139):
            pygame.draw.polygon(screen, (24, 22, 21), [(x - 4, 351), (x, 328), (x + 4, 351)])
        self._draw_eye(screen, 52, 332, .28)
        pygame.draw.line(screen, (89, 58, 39), (123, 335), (123, 402), 3)
        pygame.draw.polygon(screen, (112, 34, 25), [(124, 340), (158, 351), (124, 365)])
        # Gondor's pale citadel uses terraces, buttresses, masonry, and heraldry.
        pygame.draw.polygon(screen, (120, 128, 124), [(1129, 550), (1129, 380),
                            (1150, 360), (1150, 328), (1172, 311), (1172, 550)])
        pygame.draw.rect(screen, (166, 174, 167), (1139, 369, 123, 181))
        pygame.draw.rect(screen, (199, 201, 190), (1180, 303, 55, 247))
        pygame.draw.polygon(screen, (226, 224, 204), [(1171, 307), (1207, 257), (1244, 307)])
        pygame.draw.polygon(screen, (151, 161, 157), [(1139, 369), (1180, 338),
                            (1180, 550), (1139, 550)])
        for x in (1141, 1164, 1238):
            pygame.draw.polygon(screen, (187, 190, 181), [(x, 392), (x + 10, 375),
                                (x + 17, 550), (x, 550)])
        for y in range(332, 530, 25):
            pygame.draw.line(screen, (151, 157, 151), (1183, y), (1233, y), 1)
        pygame.draw.rect(screen, (47, 53, 52), (1153, 459, 51, 91))
        pygame.draw.ellipse(screen, (47, 53, 52), (1153, 438, 51, 44))
        pygame.draw.circle(screen, (233, 232, 214), (1207, 350), 14, 3)
        pygame.draw.line(screen, (87, 91, 91), (1247, 323), (1247, 401), 2)
        pygame.draw.polygon(screen, (53, 73, 91), [(1248, 328), (1276, 338), (1248, 350)])
        # Damage becomes visible before the base is destroyed.
        if mordor_health < .75:
            pygame.draw.lines(screen, (17, 16, 15), False,
                              [(80, 374), (68, 394), (80, 411), (73, 432)], 2)
        if mordor_health < .45:
            self._draw_flame(screen, 38, 382, 1.0)
        if gondor_health < .75:
            pygame.draw.lines(screen, (98, 104, 101), False,
                              [(1172, 394), (1182, 411), (1175, 429), (1188, 446)], 2)
        if gondor_health < .45:
            self._draw_flame(screen, 1228, 366, .9)
        self._bar(screen, pygame.Rect(24, 266, 120, 12), game.mordor.base_health / C.BASE_MAX_HEALTH,
                  (165, 47, 30))
        self._bar(screen, pygame.Rect(1136, 266, 120, 12), game.gondor.base_health / C.BASE_MAX_HEALTH,
                  (207, 210, 198))

    @staticmethod
    def _draw_flame(screen: pygame.Surface, x: int, y: int, scale: float) -> None:
        pygame.draw.polygon(screen, (165, 47, 23), [(x - int(8 * scale), y),
                            (x, y - int(28 * scale)), (x + int(9 * scale), y), (x, y + 5)])
        pygame.draw.polygon(screen, (239, 130, 31), [(x - int(4 * scale), y),
                            (x + 2, y - int(18 * scale)), (x + int(5 * scale), y), (x, y + 2)])

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
        phase = time * (6.5 + unit.kind.speed / 30) + unit.id * 1.7
        bob = int(math.sin(phase) * 2)
        stride = int(math.sin(phase) * 4)
        size = unit.kind.size
        mordor = unit.faction == "mordor"
        body = (83, 94, 65) if mordor else (201, 204, 201)
        accent = (151, 48, 30) if mordor else (52, 75, 101)
        dark = (39, 38, 34) if mordor else (55, 66, 72)
        metal = (125, 123, 109) if mordor else (221, 223, 211)
        if unit.kind.is_hero:
            body = (108, 91, 65) if mordor else (225, 220, 201)
            accent = (225, 164, 48)
        if unit.flash_timer > 0:
            body = (255, 235, 210)
        shadow_width = size * (3 if unit.kind.key in ("warg_rider", "gondor_knight") else 2)
        pygame.draw.ellipse(screen, (26, 24, 21), (x - shadow_width // 2, y + 16, shadow_width, 9))
        if unit.kind.key in ("warg_rider", "gondor_knight"):
            mount = (71, 59, 47) if mordor else (151, 151, 145)
            pygame.draw.ellipse(screen, mount, (x - 27, y - 10 + bob, 52, 24))
            head_x = x + unit.direction * 28
            pygame.draw.polygon(screen, mount, [(head_x - unit.direction * 8, y - 11 + bob),
                                (head_x + unit.direction * 11, y - 19 + bob),
                                (head_x + unit.direction * 16, y - 7 + bob), (head_x, y + 2 + bob)])
            pygame.draw.polygon(screen, dark, [(head_x - unit.direction * 2, y - 17 + bob),
                                (head_x, y - 28 + bob), (head_x + unit.direction * 7, y - 18 + bob)])
            for offset, motion in ((-17, stride), (-4, -stride), (11, -stride), (21, stride)):
                pygame.draw.line(screen, mount, (x + offset, y + 5 + bob),
                                 (x + offset + motion, y + 19), 5)
            pygame.draw.circle(screen, (220, 76, 31) if mordor else (28, 28, 26),
                               (head_x + unit.direction * 8, y - 11 + bob), 2)
        elif unit.kind.key == "olog_hai":
            pygame.draw.line(screen, (91, 65, 43), (x - unit.direction * 18, y - 34),
                             (x - unit.direction * 28, y + 8), 9)
        # Legs and body.
        pygame.draw.line(screen, dark, (x - 5, y + bob), (x - 7 - stride, y + 19), 6)
        pygame.draw.line(screen, dark, (x + 5, y + bob), (x + 7 + stride, y + 19), 6)
        pygame.draw.line(screen, (22, 22, 20), (x - 12 - stride, y + 19),
                         (x - 4 - stride, y + 19), 4)
        pygame.draw.line(screen, (22, 22, 20), (x + 4 + stride, y + 19),
                         (x + 12 + stride, y + 19), 4)
        if unit.kind.key in ("gondor_ranger", "gondor_archer"):
            cloak = (45, 76, 53) if unit.kind.key == "gondor_ranger" else accent
            pygame.draw.polygon(screen, cloak, [(x - 11, y - 29 + bob),
                                (x - unit.direction * 15, y + 8), (x + 12, y + 5)])
        pygame.draw.polygon(screen, body, [(x - size // 2, y - 26 + bob),
                                            (x + size // 2, y - 26 + bob),
                                            (x + size // 2 + 3, y + 5 + bob),
                                            (x - size // 2 - 3, y + 5 + bob)])
        pygame.draw.rect(screen, accent, (x - size // 2 - 2, y - 10 + bob, size + 4, 7))
        pygame.draw.circle(screen, body, (x, y - 36 + bob), max(7, size // 2))
        # Faction helmets and face slits sharpen silhouettes at gameplay scale.
        if mordor:
            pygame.draw.polygon(screen, dark, [(x - 10, y - 38 + bob), (x, y - 51 + bob),
                                (x + 10, y - 38 + bob), (x + 7, y - 34 + bob),
                                (x - 8, y - 34 + bob)])
            pygame.draw.line(screen, (186, 64, 31), (x + unit.direction * 2, y - 36 + bob),
                             (x + unit.direction * 7, y - 36 + bob), 2)
        else:
            pygame.draw.arc(screen, metal, (x - 10, y - 47 + bob, 20, 20), math.pi, math.tau, 5)
            pygame.draw.line(screen, metal, (x + unit.direction * 7, y - 41 + bob),
                             (x + unit.direction * 7, y - 30 + bob), 3)
        if unit.kind.ranged:
            bow_x = x + unit.direction * 14
            pygame.draw.arc(screen, (126, 82, 43), (bow_x - 8, y - 40, 16, 35),
                            -math.pi / 2, math.pi / 2, 2)
            pygame.draw.line(screen, (193, 183, 154), (bow_x, y - 39), (bow_x, y - 6), 1)
        else:
            weapon_x = x + unit.direction * 15
            attacking = unit.attack_timer > unit.kind.attack_cooldown * .55
            tip_x = weapon_x + unit.direction * (24 if attacking else 13)
            tip_y = y - 25 if attacking else y - 50
            pygame.draw.line(screen, (111, 76, 44), (weapon_x, y - 28), (tip_x, tip_y), 3)
            pygame.draw.line(screen, metal, (tip_x, tip_y),
                             (tip_x + unit.direction * 5, tip_y - 10), 4)
            if unit.kind.key in ("soldier", "boromir", "tower_guard"):
                shield_x = x - unit.direction * 12
                pygame.draw.circle(screen, dark, (shield_x, y - 15 + bob), 12)
                pygame.draw.circle(screen, metal, (shield_x, y - 15 + bob), 11, 2)
                pygame.draw.line(screen, accent, (shield_x, y - 23 + bob),
                                 (shield_x, y - 7 + bob), 2)
        if unit.kind.key in ("uruk", "tower_guard"):
            pygame.draw.polygon(screen, accent, [(x - 12, y - 43 + bob), (x, y - 56 + bob),
                                                  (x + 12, y - 43 + bob)])
        if unit.kind.key == "gondor_ranger":
            pygame.draw.polygon(screen, (48, 82, 55), [(x - 10, y - 39 + bob),
                                                       (x, y - 52 + bob),
                                                       (x + 10, y - 39 + bob)])
        if unit.kind.is_hero:
            pygame.draw.polygon(screen, (230, 175, 55), [(x, y - 76), (x + 5, y - 69),
                                (x, y - 62), (x - 5, y - 69)])
        ratio = float(unit.health) / unit.kind.max_health
        if ratio < .999 or unit.kind.is_hero:
            width = 48 if unit.kind.is_hero else 38
            self._bar(screen, pygame.Rect(x - width // 2, y - 65, width, 5), ratio,
                      (174, 50, 38) if mordor else (218, 220, 210), border=False)

    def _draw_projectile(self, screen: pygame.Surface, projectile) -> None:
        color = (236, 104, 36) if projectile.faction == "mordor" else (225, 225, 202)
        x = int(projectile.x)
        direction = 1 if projectile.faction == "mordor" else -1
        pygame.draw.line(screen, (51, 39, 30), (x - direction * 13, 450),
                         (x + direction * 10, 446), 2)
        pygame.draw.polygon(screen, color, [(x + direction * 14, 445),
                            (x + direction * 8, 441), (x + direction * 9, 449)])

    def _draw_hud(self, screen: pygame.Surface, game) -> None:
        panel = pygame.Surface((C.SCREEN_WIDTH, 120), pygame.SRCALPHA)
        panel.fill((10, 12, 13, 246))
        screen.blit(panel, (0, 600))
        pygame.draw.line(screen, (41, 31, 24), (0, 602), (C.SCREEN_WIDTH, 602), 5)
        pygame.draw.line(screen, (151, 101, 42), (0, 600), (C.SCREEN_WIDTH, 600), 1)
        mouse = pygame.mouse.get_pos()
        for i, (rect, kind) in enumerate(zip(self.CARD_RECTS, C.MORDOR_ROSTER)):
            affordable, _ = game.can_recruit("mordor", kind.key)
            hovered = rect.collidepoint(mouse)
            fill = (55, 40, 30) if affordable else (28, 30, 30)
            border = (190, 126, 46) if affordable else (69, 73, 70)
            if hovered and affordable:
                fill, border = (73, 48, 30), (235, 166, 65)
            pygame.draw.rect(screen, (4, 5, 6), rect.move(2, 3), border_radius=3)
            pygame.draw.rect(screen, fill, rect, border_radius=3)
            pygame.draw.rect(screen, border, rect, 2, 3)
            pygame.draw.line(screen, (98, 68, 38), (rect.x + 5, rect.y + 52),
                             (rect.right - 5, rect.y + 52), 1)
            # Hotkey plate and compact role icon.
            pygame.draw.rect(screen, border, (rect.x + 7, rect.y + 7, 20, 20), border_radius=2)
            key = self.tiny_font.render(str(i + 1), True, (25, 21, 17) if affordable else (145, 145, 137))
            screen.blit(key, key.get_rect(center=(rect.x + 17, rect.y + 17)))
            self._text(screen, kind.name.upper(), self.tiny_font,
                       (235, 218, 181) if affordable else (119, 122, 119), rect.x + 34, rect.y + 9)
            role = "HERO" if kind.is_hero else ("BOW" if kind.ranged else (
                "CAVALRY" if "rider" in kind.key else "HEAVY" if kind.max_health > 200 else "MELEE"))
            self._text(screen, role, self.tiny_font, (156, 159, 152), rect.x + 34, rect.y + 31)
            self._coin(screen, rect.x + 14, rect.y + 68, 7)
            self._text(screen, str(kind.cost), self.small_font,
                       (230, 174, 64) if affordable else (126, 112, 79), rect.x + 27, rect.y + 58)
        pygame.draw.line(screen, (81, 66, 43), (906, 614), (906, 692), 1)
        self._coin(screen, 930, 632, 10)
        self._text(screen, f"{int(game.mordor.gold)}", self.medium_font, (236, 184, 67), 950, 619)
        self._helmet(screen, 930, 669)
        self._text(screen, f"{game.population('mordor')} / {C.POPULATION_CAP}",
                   self.medium_font, (211, 211, 196), 950, 656)
        minutes, seconds = divmod(int(game.elapsed), 60)
        self._text(screen, "BATTLE", self.tiny_font, (132, 138, 133), 1080, 622)
        self._text(screen, f"{minutes:02}:{seconds:02}", self.medium_font, (194, 198, 190), 1080, 642)
        if game.elapsed >= C.SIEGE_PRESSURE_START and game.state == "playing":
            self._text(screen, "SIEGE PRESSURE", self.tiny_font, (220, 99, 51), 1170, 675)
        if game.message_timer > 0:
            message = self.small_font.render(game.message, True, (239, 202, 123))
            box = message.get_rect(center=(640, 583)).inflate(26, 8)
            pygame.draw.rect(screen, (17, 16, 14), box, border_radius=3)
            pygame.draw.rect(screen, (118, 84, 40), box, 1, 3)
            screen.blit(message, message.get_rect(center=box.center))

    @staticmethod
    def _coin(screen: pygame.Surface, x: int, y: int, radius: int) -> None:
        pygame.draw.circle(screen, (105, 67, 24), (x, y), radius + 1)
        pygame.draw.circle(screen, (225, 165, 54), (x, y), radius)
        pygame.draw.circle(screen, (248, 198, 84), (x - 2, y - 2), max(1, radius // 3))

    @staticmethod
    def _helmet(screen: pygame.Surface, x: int, y: int) -> None:
        pygame.draw.arc(screen, (185, 189, 180), (x - 10, y - 10, 20, 18), math.pi, math.tau, 4)
        pygame.draw.line(screen, (185, 189, 180), (x - 10, y - 1), (x - 10, y + 7), 3)
        pygame.draw.line(screen, (185, 189, 180), (x + 10, y - 1), (x + 10, y + 7), 3)
        pygame.draw.line(screen, (185, 189, 180), (x, y - 9), (x, y + 6), 2)

    def _update_and_draw_particles(self, screen: pygame.Surface, game) -> None:
        for event in game.events:
            if event.kind in ("hit", "base_hit", "death", "spawn", "tower"):
                count = {"death": 15, "base_hit": 10, "spawn": 5, "tower": 4}.get(event.kind, 7)
                for _ in range(count):
                    self.particles.append([event.x, 462.0, self._rng.uniform(-35, 35),
                                           self._rng.uniform(-90, -20), self._rng.uniform(.25, .75)])
        for particle in self.particles:
            particle[0] += particle[2] / C.FPS
            particle[1] += particle[3] / C.FPS
            particle[3] += 110 / C.FPS
            particle[4] -= 1 / C.FPS
            age = particle[4]
            color = (223, 94, 39) if age > .3 else (119, 83, 54)
            pygame.draw.circle(screen, color, (int(particle[0]), int(particle[1])), 2 if age > .2 else 1)
        self.particles = [particle for particle in self.particles if particle[4] > 0]

    def _draw_help(self, screen: pygame.Surface) -> None:
        shade = pygame.Surface((1280, 600), pygame.SRCALPHA)
        shade.fill((2, 4, 5, 150))
        screen.blit(shade, (0, 0))
        panel_rect = pygame.Rect(307, 127, 666, 398)
        pygame.draw.rect(screen, (8, 10, 10), panel_rect, border_radius=4)
        pygame.draw.rect(screen, (98, 72, 38), panel_rect, 5, 4)
        pygame.draw.rect(screen, (184, 128, 52), panel_rect.inflate(-8, -8), 1, 2)
        self._center_shadow(screen, "COMMANDER'S GUIDE", self.large_font, (225, 181, 91), 157)
        self._center(screen, "HOLD THE BLACK GATE  -  BREAK THE WHITE WALL",
                     self.tiny_font, (145, 151, 143), 205)
        lines = [
            "Destroy Gondor's fortress before the Black Gate falls.",
            "Gold arrives over time and is awarded for fallen enemies.",
            "Orc Warriors are cheap frontline troops.",
            "Orc Archers attack safely behind your line.",
            "Warg Riders are fast; Olog-hai are mighty siege troops.",
            "Lurtz is an Era 1 hero; only one may fight at a time.",
            "Controls: 1–6 recruit  •  P or Esc pause  •  F1 closes help",
        ]
        for i, line in enumerate(lines):
            color = (225, 176, 82) if i == 0 else (207, 208, 198)
            self._center(screen, line, self.small_font, color, 244 + i * 36)

    def _overlay(self, screen: pygame.Surface, title: str, subtitle: str) -> None:
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 190))
        screen.blit(shade, (0, 0))
        banner = pygame.Rect(276, 250, 728, 178)
        pygame.draw.rect(screen, (13, 14, 14), banner, border_radius=4)
        pygame.draw.rect(screen, (116, 80, 37), banner, 3, 4)
        pygame.draw.line(screen, (195, 135, 51), (319, 274), (961, 274), 1)
        pygame.draw.line(screen, (70, 56, 38), (319, 403), (961, 403), 1)
        self._center_shadow(screen, title, self.title_font, (226, 171, 73), 295)
        self._center(screen, subtitle, self.medium_font, (218, 218, 205), 368)

    @staticmethod
    def _bar(screen, rect: pygame.Rect, ratio: float, color, border: bool = True) -> None:
        pygame.draw.rect(screen, (13, 14, 14), rect)
        inner = rect.inflate(-2, -2)
        inner.width = max(0, int(inner.width * max(0, min(1, ratio))))
        pygame.draw.rect(screen, color, inner)
        if inner.width > 3:
            pygame.draw.line(screen, tuple(min(255, c + 30) for c in color),
                             (inner.x, inner.y), (inner.right - 1, inner.y), 1)
        if border:
            pygame.draw.rect(screen, (78, 62, 41), rect, 2)

    @staticmethod
    def _text(screen, text, font, color, x, y) -> None:
        screen.blit(font.render(text, True, color), (x, y))

    @staticmethod
    def _center(screen, text, font, color, y) -> None:
        image = font.render(text, True, color)
        screen.blit(image, ((C.SCREEN_WIDTH - image.get_width()) // 2, y))

    @staticmethod
    def _center_shadow(screen, text, font, color, y) -> None:
        shadow = font.render(text, True, (3, 3, 3))
        x = (C.SCREEN_WIDTH - shadow.get_width()) // 2
        screen.blit(shadow, (x + 3, y + 4))
        screen.blit(font.render(text, True, color), (x, y))