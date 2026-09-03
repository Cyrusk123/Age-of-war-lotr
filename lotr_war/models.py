"""Simulation model types. These classes do not depend on pygame."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

from . import config as C

_IDS = count()


@dataclass
class Unit:
    kind: C.UnitDef
    x: float
    health: float | None = None
    attack_timer: float = 0.0
    flash_timer: float = 0.0
    id: int = field(default_factory=lambda: next(_IDS))

    def __post_init__(self) -> None:
        if self.health is None:
            self.health = self.kind.max_health

    @property
    def faction(self) -> str:
        return self.kind.faction

    @property
    def direction(self) -> int:
        return 1 if self.faction == "mordor" else -1

    @property
    def alive(self) -> bool:
        return bool(self.health and self.health > 0)


@dataclass
class Projectile:
    faction: str
    x: float
    target_id: int
    damage: float
    speed: float
    dead: bool = False


@dataclass
class Army:
    faction: str
    gold: float = C.STARTING_GOLD
    base_health: float = C.BASE_MAX_HEALTH
    tower_timer: float = 0.0


@dataclass
class CombatEvent:
    kind: str
    x: float
    faction: str = ""
    value: float = 0.0