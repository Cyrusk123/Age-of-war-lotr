"""Game constants and data-driven faction/unit definitions."""

from __future__ import annotations

from dataclasses import dataclass

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GROUND_Y = 505
LANE_LEFT = 154.0
LANE_RIGHT = 1126.0
BASE_MAX_HEALTH = 1800.0
BASE_ATTACK_RANGE = 230.0
BASE_ATTACK_DAMAGE = 24.0
BASE_ATTACK_COOLDOWN = 2.0
STARTING_GOLD = 220.0
PASSIVE_INCOME = 8.0
POPULATION_CAP = 12
UNIT_SPACING = 12.0
SIEGE_PRESSURE_START = 180.0
SIEGE_PRESSURE_DAMAGE = 9.0


@dataclass(frozen=True)
class UnitDef:
    key: str
    name: str
    faction: str
    cost: int
    max_health: float
    damage: float
    speed: float
    attack_range: float
    attack_cooldown: float
    bounty: int
    size: int
    projectile_speed: float = 0.0
    era: int = 1
    is_hero: bool = False

    @property
    def ranged(self) -> bool:
        return self.projectile_speed > 0


MORDOR_UNITS = (
    UnitDef("orc", "Orc Warrior", "mordor", 60, 130, 19, 43, 31, 0.85, 27, 18),
    UnitDef("orc_archer", "Orc Archer", "mordor", 95, 82, 16, 36, 175, 1.20, 42, 16, 330),
    UnitDef("uruk", "Uruk-hai", "mordor", 170, 285, 35, 29, 35, 1.15, 76, 22),
    UnitDef("warg_rider", "Warg Rider", "mordor", 145, 165, 27, 58, 34, 0.90, 65, 21),
    UnitDef("olog_hai", "Olog-hai", "mordor", 240, 410, 47, 22, 42, 1.35, 110, 27),
)

MORDOR_HEROES = (
    UnitDef("lurtz", "Lurtz", "mordor", 380, 430, 43, 38, 190, 1.00, 175, 25, 380, 1, True),
)

GONDOR_UNITS = (
    UnitDef("soldier", "Gondor Soldier", "gondor", 65, 145, 18, 39, 32, 0.90, 29, 18),
    UnitDef("gondor_archer", "Gondor Archer", "gondor", 100, 88, 17, 34, 180, 1.25, 45, 16, 340),
    UnitDef("tower_guard", "Tower Guard", "gondor", 180, 310, 33, 27, 38, 1.10, 81, 23),
    UnitDef("gondor_ranger", "Gondor Ranger", "gondor", 135, 108, 24, 37, 210, 1.20, 60, 17, 365),
    UnitDef("gondor_knight", "Knight of Gondor", "gondor", 225, 345, 42, 50, 38, 1.10, 100, 24),
)

GONDOR_HEROES = (
    UnitDef("boromir", "Boromir", "gondor", 400, 520, 52, 38, 40, 0.85, 185, 25, 0, 1, True),
)

MORDOR_ROSTER = MORDOR_UNITS + MORDOR_HEROES
GONDOR_ROSTER = GONDOR_UNITS + GONDOR_HEROES
UNIT_DEFS = {unit.key: unit for unit in MORDOR_ROSTER + GONDOR_ROSTER}

MORDOR_COLORS = ((64, 72, 54), (147, 54, 35), (220, 128, 42))
GONDOR_COLORS = ((205, 210, 213), (65, 91, 118), (238, 238, 225))