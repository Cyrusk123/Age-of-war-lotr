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
MAX_QUEUE = 5
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
    train_time: float
    bounty: int
    size: int
    projectile_speed: float = 0.0

    @property
    def ranged(self) -> bool:
        return self.projectile_speed > 0


MORDOR_UNITS = (
    UnitDef("orc", "Orc Warrior", "mordor", 60, 130, 19, 43, 31, 0.85, 1.15, 27, 18),
    UnitDef("orc_archer", "Orc Archer", "mordor", 95, 82, 16, 36, 175, 1.20, 1.75, 42, 16, 330),
    UnitDef("uruk", "Uruk-hai", "mordor", 170, 285, 35, 29, 35, 1.15, 2.75, 76, 22),
)

GONDOR_UNITS = (
    UnitDef("soldier", "Gondor Soldier", "gondor", 65, 145, 18, 39, 32, 0.90, 1.25, 29, 18),
    UnitDef("gondor_archer", "Gondor Archer", "gondor", 100, 88, 17, 34, 180, 1.25, 1.85, 45, 16, 340),
    UnitDef("tower_guard", "Tower Guard", "gondor", 180, 310, 33, 27, 38, 1.10, 2.90, 81, 23),
)

UNIT_DEFS = {unit.key: unit for unit in MORDOR_UNITS + GONDOR_UNITS}

MORDOR_COLORS = ((64, 72, 54), (147, 54, 35), (220, 128, 42))
GONDOR_COLORS = ((205, 210, 213), (65, 91, 118), (238, 238, 225))