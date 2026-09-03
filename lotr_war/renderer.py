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
        """Render a readable, equipment-rich model with a unique class silhouette."""
        x, y, direction = int(unit.x), C.GROUND_Y, unit.direction
        phase = time * (5.4 + unit.kind.speed / 24) + unit.id * 1.73
        attacking = unit.attack_timer > unit.kind.attack_cooldown * .52
        key = unit.kind.key
        heights = {"warg_rider": 79, "gondor_knight": 84, "olog_hai": 88,
                   "uruk": 73, "tower_guard": 82, "lurtz": 81, "boromir": 79}
        height = heights.get(key, 68)
        shadow_width = {"warg_rider": 76, "gondor_knight": 82,
                        "olog_hai": 62}.get(key, 42 + unit.kind.size // 2)
        pygame.draw.ellipse(screen, (19, 18, 16), (x - shadow_width // 2, y + 14,
                                                  shadow_width, 10))

        if key in ("warg_rider", "gondor_knight"):
            self._draw_mounted_unit(screen, unit, x, y, direction, phase, attacking)
        elif key == "olog_hai":
            self._draw_olog(screen, unit, x, y, direction, phase, attacking)
        else:
            self._draw_humanoid(screen, unit, x, y, direction, phase, attacking)

        ratio = float(unit.health) / unit.kind.max_health
        if ratio < .999 or unit.kind.is_hero:
            width = 52 if unit.kind.is_hero else max(38, unit.kind.size + 18)
            bar_y = y - height - 10
            self._bar(screen, pygame.Rect(x - width // 2, bar_y, width, 5), ratio,
                      (183, 53, 35) if unit.faction == "mordor" else (224, 226, 211),
                      border=False)
            if unit.kind.is_hero:
                pygame.draw.circle(screen, (225, 170, 57), (x - width // 2 - 4, bar_y + 2), 3)

    @staticmethod
    def _limb(screen: pygame.Surface, color, start, joint, end, width: int) -> None:
        """Draw a jointed limb with round connections rather than a stick line."""
        pygame.draw.line(screen, (24, 23, 21), start, joint, width + 3)
        pygame.draw.line(screen, (24, 23, 21), joint, end, width + 3)
        pygame.draw.line(screen, color, start, joint, width)
        pygame.draw.line(screen, color, joint, end, width)
        pygame.draw.circle(screen, color, joint, max(2, width // 2))

    @staticmethod
    def _draw_sword(screen: pygame.Surface, hand, tip, metal, broad: bool = False) -> None:
        hx, hy = hand
        tx, ty = tip
        pygame.draw.line(screen, (104, 67, 39), (hx, hy), (hx + (tx - hx) * .18, hy + (ty - hy) * .18), 4)
        pygame.draw.line(screen, (54, 48, 40), (hx - 4, hy - 2), (hx + 5, hy + 3), 3)
        pygame.draw.line(screen, (36, 36, 34), (hx, hy), (tx, ty), 7 if broad else 5)
        pygame.draw.line(screen, metal, (hx, hy), (tx, ty), 4 if broad else 2)
        pygame.draw.circle(screen, (189, 143, 57), (hx, hy), 2)

    @staticmethod
    def _draw_bow(screen: pygame.Surface, hand, direction: int, drawn: bool,
                  longbow: bool = False) -> None:
        hx, hy = hand
        radius = 23 if longbow else 19
        bow_x = hx + direction * (7 if drawn else 3)
        rect = pygame.Rect(bow_x - radius // 2, hy - radius, radius, radius * 2)
        if direction > 0:
            pygame.draw.arc(screen, (151, 102, 52), rect, -math.pi / 2, math.pi / 2, 3)
        else:
            pygame.draw.arc(screen, (151, 102, 52), rect, math.pi / 2, math.pi * 1.5, 3)
        string_x = hx - direction * (8 if drawn else 0)
        pygame.draw.line(screen, (211, 203, 174), (bow_x, hy - radius), (string_x, hy), 1)
        pygame.draw.line(screen, (211, 203, 174), (string_x, hy), (bow_x, hy + radius), 1)
        if drawn:
            pygame.draw.line(screen, (83, 58, 37), (string_x, hy),
                             (bow_x + direction * 17, hy), 2)

    @staticmethod
    def _draw_shield(screen: pygame.Surface, x: int, y: int, style: str,
                     face, rim, emblem) -> None:
        if style == "tower":
            points = [(x - 10, y - 17), (x + 10, y - 17), (x + 9, y + 11),
                      (x, y + 19), (x - 9, y + 11)]
            pygame.draw.polygon(screen, (25, 27, 27), points)
            pygame.draw.polygon(screen, face, points)
            pygame.draw.lines(screen, rim, True, points, 2)
        elif style == "kite":
            points = [(x, y - 16), (x + 13, y - 8), (x + 9, y + 13),
                      (x, y + 21), (x - 9, y + 13), (x - 13, y - 8)]
            pygame.draw.polygon(screen, face, points)
            pygame.draw.lines(screen, rim, True, points, 2)
        else:
            pygame.draw.circle(screen, (25, 27, 27), (x + 1, y + 2), 15)
            pygame.draw.circle(screen, face, (x, y), 14)
            pygame.draw.circle(screen, rim, (x, y), 14, 2)
        pygame.draw.line(screen, emblem, (x, y - 8), (x, y + 9), 2)
        pygame.draw.line(screen, emblem, (x - 5, y - 1), (x + 5, y - 1), 1)

    def _draw_humanoid(self, screen: pygame.Surface, unit: Unit, x: int, y: int,
                       d: int, phase: float, attacking: bool) -> None:
        key = unit.kind.key
        mordor = unit.faction == "mordor"
        heavy = key in ("uruk", "tower_guard")
        hero = unit.kind.is_hero
        bob = int(math.sin(phase * 2) * (1 if heavy else 2))
        stride = int(math.sin(phase) * (3 if heavy else 5))
        if attacking:
            stride = -d * 2
        base_y = y + bob

        skin = (91, 99, 67) if mordor else (204, 174, 142)
        leather = (61, 47, 35) if mordor else (78, 65, 51)
        dark = (37, 35, 32) if mordor else (43, 50, 54)
        metal = (119, 117, 103) if mordor else (207, 212, 207)
        bright = (165, 157, 132) if mordor else (239, 239, 221)
        cloth = (126, 43, 31) if mordor else (42, 62, 83)
        if key == "gondor_ranger":
            cloth, leather = (42, 72, 49), (70, 57, 40)
        elif key == "gondor_archer":
            cloth = (64, 79, 89)
        elif key == "lurtz":
            skin, cloth, metal = (105, 100, 70), (87, 35, 27), (138, 130, 108)
        elif key == "boromir":
            cloth, metal, bright = (101, 47, 37), (211, 207, 188), (239, 223, 177)
        if unit.flash_timer > 0:
            skin = cloth = metal = bright = (255, 238, 213)

        # Cloaks and quivers sit behind the body and establish the broad silhouette.
        if key in ("gondor_ranger", "gondor_archer", "tower_guard", "boromir", "lurtz"):
            cloak = {"gondor_ranger": (37, 68, 45), "gondor_archer": (45, 61, 69),
                     "tower_guard": (25, 31, 37), "boromir": (102, 43, 34),
                     "lurtz": (55, 37, 29)}[key]
            flutter = int(math.sin(phase + .8) * 3)
            pygame.draw.polygon(screen, (25, 25, 23), [(x - d * 7, base_y - 48),
                                (x - d * (18 + flutter), base_y + 5), (x + d * 7, base_y + 2)])
            pygame.draw.polygon(screen, cloak, [(x - d * 6, base_y - 47),
                                (x - d * (15 + flutter), base_y + 3), (x + d * 7, base_y)])
        if unit.kind.ranged:
            qx = x - d * 11
            pygame.draw.line(screen, (70, 48, 31), (qx, base_y - 42), (qx - d * 3, base_y - 4), 6)
            for offset in (-3, 1, 5):
                pygame.draw.line(screen, (116, 78, 40), (qx + offset, base_y - 44),
                                 (qx + offset + d * 3, base_y - 55), 2)
                pygame.draw.polygon(screen, (136, 123, 88), [(qx + offset + d * 3, base_y - 57),
                                    (qx + offset, base_y - 53), (qx + offset + d * 6, base_y - 52)])

        # Articulated legs, armored boots, and a split tunic avoid the old block body.
        leg_color = dark if heavy else leather
        self._limb(screen, leg_color, (x - 6, base_y - 5), (x - 6 - stride // 2, base_y + 8),
                   (x - 7 - stride, y + 17), 6 if heavy else 5)
        self._limb(screen, leg_color, (x + 6, base_y - 5), (x + 6 + stride // 2, base_y + 8),
                   (x + 7 + stride, y + 17), 6 if heavy else 5)
        pygame.draw.line(screen, (24, 24, 22), (x - 8 - stride, y + 17),
                         (x - 15 - stride * d // 2, y + 18), 5)
        pygame.draw.line(screen, (24, 24, 22), (x + 8 + stride, y + 17),
                         (x + 15 + stride * d // 2, y + 18), 5)

        shoulder = 17 if heavy or hero else 13
        pygame.draw.polygon(screen, dark, [(x - shoulder, base_y - 43), (x - 10, base_y - 52),
                            (x + 10, base_y - 52), (x + shoulder, base_y - 43),
                            (x + 11, base_y - 9), (x, base_y - 3), (x - 11, base_y - 9)])
        pygame.draw.polygon(screen, cloth, [(x - 10, base_y - 43), (x, base_y - 49),
                            (x + 10, base_y - 43), (x + 9, base_y - 13),
                            (x, base_y - 7), (x - 9, base_y - 13)])
        # Mail/plate panels, belt, shoulder armor, and faction heraldry.
        if heavy or key in ("soldier", "boromir", "lurtz"):
            pygame.draw.polygon(screen, metal, [(x - 10, base_y - 43), (x, base_y - 47),
                                (x + 10, base_y - 43), (x + 8, base_y - 22),
                                (x, base_y - 17), (x - 8, base_y - 22)])
            for mail_y in range(base_y - 37, base_y - 20, 5):
                pygame.draw.line(screen, dark, (x - 7, mail_y), (x + 7, mail_y), 1)
        pygame.draw.rect(screen, leather, (x - 12, base_y - 17, 24, 5))
        pygame.draw.circle(screen, (193, 143, 52), (x, base_y - 15), 2)
        if heavy:
            pygame.draw.ellipse(screen, metal, (x - 21, base_y - 49, 14, 10))
            pygame.draw.ellipse(screen, metal, (x + 7, base_y - 49, 14, 10))

        # Head, hair/hood, and helmets use profiles rather than featureless circles.
        head_y = base_y - 59
        pygame.draw.ellipse(screen, (30, 28, 25), (x - 8, head_y - 8, 18, 21))
        pygame.draw.ellipse(screen, skin, (x - 7, head_y - 8, 15, 18))
        pygame.draw.polygon(screen, skin, [(x + d * 6, head_y - 3),
                            (x + d * 11, head_y + 1), (x + d * 6, head_y + 3)])
        if key == "gondor_ranger":
            pygame.draw.polygon(screen, (35, 65, 43), [(x - 12, head_y + 5),
                                (x, head_y - 17), (x + 12, head_y + 5), (x + 8, head_y + 12),
                                (x - 8, head_y + 12)])
            pygame.draw.ellipse(screen, (20, 29, 22), (x - 7, head_y - 5, 14, 13), 2)
        elif key in ("lurtz", "boromir"):
            hair = (31, 27, 23) if key == "lurtz" else (91, 67, 43)
            pygame.draw.arc(screen, hair, (x - 10, head_y - 12, 20, 24), math.pi, math.tau, 7)
            pygame.draw.line(screen, hair, (x - d * 7, head_y - 5), (x - d * 10, head_y + 10), 4)
        elif mordor:
            crest = 12 if key == "uruk" else 7
            pygame.draw.polygon(screen, dark, [(x - 10, head_y + 2), (x - 5, head_y - 10),
                                (x, head_y - 10 - crest), (x + 9, head_y - 6),
                                (x + 10, head_y + 7), (x - 8, head_y + 8)])
            pygame.draw.line(screen, (168, 56, 36), (x + d * 2, head_y), (x + d * 7, head_y), 2)
        else:
            pygame.draw.arc(screen, metal, (x - 10, head_y - 12, 20, 21), math.pi, math.tau, 6)
            pygame.draw.line(screen, metal, (x - 9, head_y - 2), (x - 8, head_y + 9), 4)
            pygame.draw.line(screen, metal, (x + 9, head_y - 2), (x + 8, head_y + 9), 4)
            pygame.draw.line(screen, bright, (x + d * 7, head_y - 4), (x + d * 7, head_y + 7), 2)
            if key == "tower_guard":
                pygame.draw.polygon(screen, bright, [(x - 3, head_y - 10), (x, head_y - 25),
                                    (x + 4, head_y - 10)])

        hand_y = base_y - 30
        if unit.kind.ranged:
            front_hand = (x + d * 16, hand_y)
            rear_hand = (x - d * (8 if attacking else 1), hand_y)
            self._limb(screen, leather, (x + d * 8, base_y - 43),
                       (x + d * 13, hand_y - 5), front_hand, 5)
            self._limb(screen, leather, (x - d * 8, base_y - 42),
                       (x - d * 11, hand_y - 3), rear_hand, 5)
            self._draw_bow(screen, front_hand, d, attacking, key in ("gondor_ranger", "lurtz"))
        elif key == "tower_guard":
            hand = (x + d * 10, hand_y)
            self._limb(screen, metal, (x + d * 9, base_y - 43),
                       (x + d * 13, hand_y - 5), hand, 6)
            spear_top = (x + d * (27 if attacking else 15), base_y - (34 if attacking else 83))
            spear_bottom = (x - d * 9, base_y + 8)
            pygame.draw.line(screen, (99, 70, 43), spear_bottom, spear_top, 4)
            pygame.draw.polygon(screen, bright, [spear_top,
                                (spear_top[0] - d * 5, spear_top[1] + 12),
                                (spear_top[0] + d * 3, spear_top[1] + 9)])
            self._draw_shield(screen, x - d * 13, base_y - 23, "tower",
                              (36, 42, 48), bright, (218, 218, 199))
        else:
            front_hand = (x + d * 15, hand_y + (4 if attacking else 0))
            elbow = (x + d * (18 if attacking else 12), base_y - (39 if attacking else 31))
            self._limb(screen, metal if heavy else leather, (x + d * 9, base_y - 43),
                       elbow, front_hand, 6 if heavy else 5)
            tip = (x + d * (43 if attacking else 27),
                   base_y - (31 if attacking else 68))
            self._draw_sword(screen, front_hand, tip, bright, key in ("uruk", "lurtz"))
            if key in ("soldier", "boromir"):
                style = "round" if key == "boromir" else "kite"
                face = (71, 79, 83) if key == "soldier" else (116, 45, 36)
                self._draw_shield(screen, x - d * 14, base_y - 25, style,
                                  face, bright, (225, 222, 197))
            elif key == "orc":
                self._draw_shield(screen, x - d * 13, base_y - 23, "round",
                                  (73, 48, 35), metal, (151, 48, 30))

        if hero:
            # A grounded gold standard behind the shoulders reads as rank without a floating icon.
            standard_x = x - d * 18
            pygame.draw.line(screen, (119, 78, 38), (standard_x, base_y - 8),
                             (standard_x, base_y - 79), 2)
            pygame.draw.polygon(screen, (190, 132, 39), [(standard_x, base_y - 77),
                                (standard_x + d * 14, base_y - 71),
                                (standard_x, base_y - 64)])
            if key == "boromir":
                pygame.draw.arc(screen, (208, 180, 103),
                                (x - d * 19 - 6, base_y - 42, 12, 22), 0, math.tau, 3)

    def _draw_mounted_unit(self, screen: pygame.Surface, unit: Unit, x: int, y: int,
                           d: int, phase: float, attacking: bool) -> None:
        warg = unit.kind.key == "warg_rider"
        bob = int(math.sin(phase * 2) * 2)
        gallop = int(math.sin(phase) * 8)
        body = (62, 52, 43) if warg else (157, 161, 157)
        shade = (35, 32, 29) if warg else (86, 94, 94)
        light = (92, 78, 58) if warg else (205, 207, 198)
        armor = (72, 66, 57) if warg else (194, 200, 198)
        if unit.flash_timer > 0:
            body = light = armor = (255, 238, 213)

        # Four articulated legs are widely spaced so the mount reads at gameplay scale.
        for ox, motion in ((-24, gallop), (-9, -gallop), (12, -gallop), (25, gallop)):
            knee = (x + ox + motion // 3, y + 3 + bob)
            hoof = (x + ox + motion, y + 18)
            self._limb(screen, shade, (x + ox, y - 8 + bob), knee, hoof, 6 if warg else 5)
            pygame.draw.line(screen, (25, 25, 23), hoof, (hoof[0] + d * 5, hoof[1]), 4)
        pygame.draw.ellipse(screen, shade, (x - 33, y - 25 + bob, 65, 31))
        pygame.draw.ellipse(screen, body, (x - 31, y - 27 + bob, 62, 28))
        pygame.draw.polygon(screen, light, [(x - 21, y - 25 + bob), (x + 20, y - 25 + bob),
                            (x + 28, y - 13 + bob), (x - 27, y - 13 + bob)])

        neck_x = x + d * 28
        if warg:
            pygame.draw.polygon(screen, shade, [(neck_x - d * 9, y - 22 + bob),
                                (neck_x + d * 7, y - 39 + bob), (neck_x + d * 17, y - 26 + bob),
                                (neck_x + d * 10, y - 10 + bob)])
            muzzle = (neck_x + d * 18, y - 25 + bob)
            pygame.draw.polygon(screen, body, [(neck_x, y - 34 + bob), muzzle,
                                (neck_x + d * 23, y - 17 + bob), (neck_x - d * 2, y - 17 + bob)])
            pygame.draw.polygon(screen, shade, [(neck_x - d * 2, y - 34 + bob),
                                (neck_x, y - 47 + bob), (neck_x + d * 7, y - 35 + bob)])
            pygame.draw.polygon(screen, (222, 210, 172), [(neck_x + d * 18, y - 18 + bob),
                                (neck_x + d * 22, y - 13 + bob), (neck_x + d * 14, y - 16 + bob)])
            pygame.draw.circle(screen, (222, 69, 30), (neck_x + d * 9, y - 29 + bob), 2)
            # Ragged tail.
            pygame.draw.line(screen, shade, (x - d * 30, y - 20 + bob),
                             (x - d * 47, y - 31 + gallop // 3), 6)
        else:
            pygame.draw.polygon(screen, body, [(neck_x - d * 10, y - 22 + bob),
                                (neck_x + d * 2, y - 47 + bob), (neck_x + d * 13, y - 43 + bob),
                                (neck_x + d * 16, y - 24 + bob), (neck_x + d * 5, y - 12 + bob)])
            pygame.draw.polygon(screen, body, [(neck_x + d * 4, y - 45 + bob),
                                (neck_x + d * 19, y - 48 + bob), (neck_x + d * 23, y - 42 + bob),
                                (neck_x + d * 11, y - 36 + bob)])
            pygame.draw.polygon(screen, shade, [(neck_x, y - 46 + bob),
                                (neck_x - d * 3, y - 58 + bob), (neck_x + d * 5, y - 48 + bob)])
            pygame.draw.circle(screen, (25, 25, 23), (neck_x + d * 13, y - 44 + bob), 2)
            pygame.draw.line(screen, shade, (x - d * 30, y - 23 + bob),
                             (x - d * 44, y - 4 + gallop // 4), 5)
        # Barding and saddle separate the rider from the animal.
        barding = (105, 39, 30) if warg else (43, 59, 77)
        pygame.draw.polygon(screen, barding, [(x - 19, y - 27 + bob), (x + 17, y - 27 + bob),
                            (x + 20, y - 6 + bob), (x - 17, y - 7 + bob)])
        pygame.draw.rect(screen, (72, 48, 34), (x - 15, y - 32 + bob, 30, 8))
        pygame.draw.line(screen, (72, 48, 34), (x, y - 28 + bob), (x + d * 11, y - 6 + bob), 3)

        rider_y = y - 31 + bob
        skin = (87, 94, 64) if warg else (201, 171, 139)
        rider_metal = (111, 107, 94) if warg else (217, 221, 214)
        rider_dark = (38, 35, 31) if warg else (39, 47, 53)
        pygame.draw.polygon(screen, rider_dark, [(x - 13, rider_y - 27), (x, rider_y - 34),
                            (x + 13, rider_y - 27), (x + 10, rider_y), (x - 10, rider_y)])
        pygame.draw.polygon(screen, rider_metal, [(x - 10, rider_y - 27), (x, rider_y - 31),
                            (x + 10, rider_y - 27), (x + 7, rider_y - 7), (x - 7, rider_y - 7)])
        pygame.draw.ellipse(screen, skin, (x - 7, rider_y - 46, 15, 17))
        if warg:
            pygame.draw.polygon(screen, rider_dark, [(x - 9, rider_y - 39), (x, rider_y - 56),
                                (x + 9, rider_y - 39), (x + 7, rider_y - 33), (x - 8, rider_y - 33)])
            hand = (x + d * 13, rider_y - 20)
            tip = (x + d * (45 if attacking else 29), rider_y - (18 if attacking else 55))
            self._draw_sword(screen, hand, tip, (154, 148, 127), True)
        else:
            pygame.draw.arc(screen, rider_metal, (x - 9, rider_y - 50, 18, 18), math.pi, math.tau, 6)
            pygame.draw.line(screen, rider_metal, (x + d * 7, rider_y - 42),
                             (x + d * 7, rider_y - 32), 3)
            hand = (x + d * 12, rider_y - 20)
            lance_tip = (x + d * (61 if attacking else 33), rider_y - (18 if attacking else 69))
            pygame.draw.line(screen, (104, 73, 43), (x - d * 13, rider_y + 3), lance_tip, 4)
            pygame.draw.polygon(screen, (231, 231, 215), [lance_tip,
                                (lance_tip[0] - d * 8, lance_tip[1] + 12),
                                (lance_tip[0] + d * 3, lance_tip[1] + 9)])
            self._draw_shield(screen, x - d * 13, rider_y - 17, "kite",
                              (45, 58, 72), rider_metal, (230, 228, 207))

    def _draw_olog(self, screen: pygame.Surface, unit: Unit, x: int, y: int,
                   d: int, phase: float, attacking: bool) -> None:
        bob = int(math.sin(phase) * 1.5)
        skin = (91, 96, 69)
        dark_skin = (60, 66, 51)
        armor = (75, 69, 59)
        metal = (126, 119, 99)
        if unit.flash_timer > 0:
            skin = dark_skin = armor = metal = (255, 238, 213)
        base_y = y + bob
        # Massive bent legs and long knuckle-dragging arms define troll proportions.
        self._limb(screen, dark_skin, (x - 12, base_y - 18), (x - 17, base_y + 1),
                   (x - 20, y + 16), 12)
        self._limb(screen, dark_skin, (x + 12, base_y - 18), (x + 17, base_y + 1),
                   (x + 20, y + 16), 12)
        pygame.draw.line(screen, (27, 27, 24), (x - 25, y + 17), (x - 9, y + 17), 7)
        pygame.draw.line(screen, (27, 27, 24), (x + 9, y + 17), (x + 27, y + 17), 7)
        pygame.draw.ellipse(screen, dark_skin, (x - 29, base_y - 67, 58, 56))
        pygame.draw.polygon(screen, skin, [(x - 25, base_y - 58), (x - 14, base_y - 73),
                            (x + 15, base_y - 71), (x + 27, base_y - 48),
                            (x + 18, base_y - 17), (x - 18, base_y - 17)])
        pygame.draw.polygon(screen, armor, [(x - 27, base_y - 57), (x - 9, base_y - 70),
                            (x + 4, base_y - 65), (x + 22, base_y - 54),
                            (x + 13, base_y - 32), (x - 18, base_y - 34)])
        pygame.draw.lines(screen, metal, False, [(x - 20, base_y - 52),
                          (x + 13, base_y - 43), (x - 12, base_y - 35)], 4)
        pygame.draw.ellipse(screen, skin, (x - 11 + d * 3, base_y - 83, 24, 22))
        pygame.draw.polygon(screen, armor, [(x - 11, base_y - 74), (x - 7, base_y - 88),
                            (x + 11, base_y - 84), (x + 14, base_y - 71)])
        pygame.draw.circle(screen, (196, 70, 32), (x + d * 8, base_y - 76), 2)
        rear_hand = (x - d * 32, base_y - 6)
        self._limb(screen, skin, (x - d * 20, base_y - 55),
                   (x - d * 29, base_y - 31), rear_hand, 11)
        front_hand = (x + d * 31, base_y - (31 if attacking else 9))
        self._limb(screen, skin, (x + d * 20, base_y - 55),
                   (x + d * 30, base_y - 35), front_hand, 12)
        club_tip = (x + d * (58 if attacking else 43),
                    base_y - (28 if attacking else 63))
        pygame.draw.line(screen, (61, 43, 30), rear_hand, club_tip, 11)
        pygame.draw.line(screen, (111, 73, 40), rear_hand, club_tip, 6)
        pygame.draw.circle(screen, (66, 57, 47), club_tip, 10)
        for angle in (-8, 0, 8):
            pygame.draw.line(screen, metal, club_tip,
                             (club_tip[0] + d * 12, club_tip[1] + angle), 3)

    def _draw_projectile(self, screen: pygame.Surface, projectile) -> None:
        color = (236, 104, 36) if projectile.faction == "mordor" else (225, 225, 202)
        x = int(projectile.x)
        direction = 1 if projectile.faction == "mordor" else -1
        pygame.draw.line(screen, (51, 39, 30), (x - direction * 15, 456),
                         (x + direction * 11, 452), 2)
        pygame.draw.line(screen, (166, 145, 104), (x - direction * 14, 456),
                         (x - direction * 19, 451), 1)
        pygame.draw.polygon(screen, color, [(x + direction * 16, 451),
                            (x + direction * 9, 447), (x + direction * 10, 455)])

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
            self._draw_card_portrait(screen, kind, rect.right - 20, rect.bottom - 8, affordable)
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
    def _draw_card_portrait(screen: pygame.Surface, kind, x: int, y: int,
                            enabled: bool) -> None:
        """Add a compact roster silhouette without competing with card text."""
        ink = (191, 149, 83) if enabled else (77, 81, 78)
        shade = (58, 42, 31) if enabled else (42, 44, 43)
        pygame.draw.ellipse(screen, (18, 17, 16), (x - 17, y - 3, 34, 5))
        if kind.key == "warg_rider":
            pygame.draw.ellipse(screen, shade, (x - 17, y - 14, 31, 11))
            pygame.draw.polygon(screen, shade, [(x + 10, y - 13), (x + 18, y - 19),
                                (x + 20, y - 9), (x + 13, y - 4)])
            pygame.draw.line(screen, ink, (x - 9, y - 6), (x - 12, y), 3)
            pygame.draw.line(screen, ink, (x + 7, y - 6), (x + 11, y), 3)
            pygame.draw.circle(screen, ink, (x, y - 23), 4)
            pygame.draw.polygon(screen, ink, [(x - 5, y - 20), (x + 5, y - 20),
                                (x + 7, y - 10), (x - 7, y - 10)])
        elif kind.key == "olog_hai":
            pygame.draw.line(screen, shade, (x - 8, y - 14), (x - 12, y), 7)
            pygame.draw.line(screen, shade, (x + 8, y - 14), (x + 12, y), 7)
            pygame.draw.ellipse(screen, ink, (x - 13, y - 32, 26, 22))
            pygame.draw.circle(screen, ink, (x + 3, y - 34), 6)
            pygame.draw.line(screen, shade, (x + 11, y - 24), (x + 20, y - 4), 6)
        else:
            broad = kind.key in ("uruk", "lurtz")
            half = 8 if broad else 6
            pygame.draw.line(screen, shade, (x - 4, y - 10), (x - 7, y), 4)
            pygame.draw.line(screen, shade, (x + 4, y - 10), (x + 7, y), 4)
            pygame.draw.polygon(screen, ink, [(x - half, y - 26), (x, y - 30),
                                (x + half, y - 26), (x + half + 2, y - 10),
                                (x - half - 2, y - 10)])
            pygame.draw.circle(screen, ink, (x, y - 34), 5)
            if kind.ranged:
                pygame.draw.arc(screen, ink, (x + 5, y - 31, 12, 25),
                                -math.pi / 2, math.pi / 2, 2)
                pygame.draw.line(screen, ink, (x + 11, y - 31), (x + 11, y - 7), 1)
            else:
                pygame.draw.line(screen, ink, (x + 7, y - 21), (x + 16, y - 39), 3)
            if kind.is_hero:
                pygame.draw.line(screen, (221, 169, 56), (x - 11, y - 9),
                                 (x - 11, y - 42), 2)
                pygame.draw.polygon(screen, (221, 169, 56), [(x - 11, y - 41),
                                    (x - 2, y - 37), (x - 11, y - 32)])

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