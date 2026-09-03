"""Adaptive, economy-respecting Gondor recruitment AI."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from . import config as C

if TYPE_CHECKING:
    from .simulation import GameSimulation


class GondorAI:
    def __init__(self, seed: int = 7) -> None:
        self.random = random.Random(seed)
        self.decision_timer = 1.4

    def update(self, game: "GameSimulation", dt: float) -> None:
        self.decision_timer -= dt
        if self.decision_timer > 0 or game.state != "playing":
            return
        pressure = sum(1 for u in game.units if u.faction == "mordor" and u.x > 720)
        self.decision_timer = max(0.7, 1.65 - game.elapsed / 180) + self.random.random() * 0.45
        self.try_recruit(game, pressure)

    def choose_unit(self, game: "GameSimulation", pressure: int = 0) -> str:
        enemies = [u for u in game.units if u.faction == "mordor"]
        allies = [u for u in game.units if u.faction == "gondor"]
        enemy_melee = sum(not u.kind.ranged for u in enemies)
        ally_melee = sum(not u.kind.ranged for u in allies)
        ally_archers = sum(u.kind.ranged for u in allies)

        if pressure >= 3 and game.gondor.gold >= C.UNIT_DEFS["tower_guard"].cost:
            return "tower_guard"
        if (game.elapsed >= 45 and not any(u.kind.key == "boromir" for u in allies)
                and game.gondor.gold >= C.UNIT_DEFS["boromir"].cost):
            return "boromir"
        if ally_melee <= ally_archers and game.gondor.gold >= C.UNIT_DEFS["soldier"].cost:
            return "soldier"
        if enemy_melee >= 2 and ally_archers < 3:
            if game.gondor.gold >= C.UNIT_DEFS["gondor_ranger"].cost:
                return "gondor_ranger"
            if game.gondor.gold >= C.UNIT_DEFS["gondor_archer"].cost:
                return "gondor_archer"
        if (game.elapsed > 70 and game.gondor.gold >= C.UNIT_DEFS["gondor_knight"].cost
                and self.random.random() < 0.35):
            return "gondor_knight"
        if game.elapsed > 55 and game.gondor.gold >= C.UNIT_DEFS["tower_guard"].cost and self.random.random() < 0.45:
            return "tower_guard"
        return "gondor_archer" if self.random.random() < 0.3 else "soldier"

    def try_recruit(self, game: "GameSimulation", pressure: int = 0) -> bool:
        key = self.choose_unit(game, pressure)
        if game.recruit("gondor", key):
            return True
        # Do not stall when the preferred counter is unaffordable.
        return game.recruit("gondor", "soldier")