"""Frame-rate-independent lane battle simulation."""

from __future__ import annotations

import random

from . import config as C
from .ai import GondorAI
from .models import Army, CombatEvent, Projectile, Unit


class GameSimulation:
    def __init__(self, seed: int = 7, enable_ai: bool = True) -> None:
        self.random = random.Random(seed)
        self.mordor = Army("mordor")
        self.gondor = Army("gondor")
        self.units: list[Unit] = []
        self.projectiles: list[Projectile] = []
        self.events: list[CombatEvent] = []
        self.elapsed = 0.0
        self.state = "playing"
        self.message = "The assault begins"
        self.message_timer = 2.5
        self.ai = GondorAI(seed + 1) if enable_ai else None

    def army(self, faction: str) -> Army:
        if faction == "mordor":
            return self.mordor
        if faction == "gondor":
            return self.gondor
        raise ValueError(f"Unknown faction: {faction}")

    def population(self, faction: str) -> int:
        self.army(faction)  # Validate the faction name.
        return sum(u.faction == faction for u in self.units)

    def can_recruit(self, faction: str, key: str) -> tuple[bool, str]:
        kind = C.UNIT_DEFS.get(key)
        if not kind or kind.faction != faction:
            return False, "Unit unavailable"
        army = self.army(faction)
        if kind.is_hero and any(unit.kind.key == key for unit in self.units):
            return False, f"{kind.name} is already deployed"
        if self.population(faction) >= C.POPULATION_CAP:
            return False, "Population limit reached"
        if army.gold < kind.cost:
            return False, "Not enough gold"
        if self.state != "playing":
            return False, "The battle is over"
        return True, ""

    def recruit(self, faction: str, key: str) -> bool:
        allowed, reason = self.can_recruit(faction, key)
        if not allowed:
            if faction == "mordor":
                self.message, self.message_timer = reason, 1.5
            return False
        army, kind = self.army(faction), C.UNIT_DEFS[key]
        army.gold -= kind.cost
        self.spawn(key)
        if faction == "mordor":
            self.message, self.message_timer = f"Deployed {kind.name}", 1.2
        return True

    def spawn(self, key: str, x: float | None = None) -> Unit:
        kind = C.UNIT_DEFS[key]
        spawn_x = C.LANE_LEFT if kind.faction == "mordor" else C.LANE_RIGHT
        unit = Unit(kind, spawn_x if x is None else x)
        self.units.append(unit)
        self.events.append(CombatEvent("spawn", unit.x, unit.faction))
        return unit

    def update(self, dt: float) -> None:
        if self.state != "playing" or dt <= 0:
            return
        # Avoid simulation tunnelling after a paused/debugged frame.
        remaining = min(dt, 0.25)
        while remaining > 0:
            step = min(remaining, 1 / 30)
            self._step(step)
            remaining -= step

    def _step(self, dt: float) -> None:
        self.elapsed += dt
        self.events.clear()
        self.message_timer = max(0.0, self.message_timer - dt)
        self.mordor.gold += C.PASSIVE_INCOME * dt
        self.gondor.gold += C.PASSIVE_INCOME * dt * 1.03
        if self.ai:
            self.ai.update(self, dt)
        for unit in list(self.units):
            unit.attack_timer = max(0.0, unit.attack_timer - dt)
            unit.flash_timer = max(0.0, unit.flash_timer - dt)
            self._update_unit(unit, dt)
        self._update_projectiles(dt)
        self._update_towers(dt)
        self._remove_dead()
        self._update_siege_pressure(dt)
        self._check_game_over()

    def _nearest_enemy_ahead(self, unit: Unit) -> Unit | None:
        enemies = [u for u in self.units if u.alive and u.faction != unit.faction]
        if not enemies:
            return None
        return min(enemies, key=lambda other: abs(other.x - unit.x))

    def _blocked_by_ally(self, unit: Unit) -> bool:
        for ally in self.units:
            if ally is unit or ally.faction != unit.faction or not ally.alive:
                continue
            ahead = (ally.x - unit.x) * unit.direction
            if 0 < ahead < unit.kind.size + ally.kind.size + C.UNIT_SPACING:
                return True
        return False

    def _update_unit(self, unit: Unit, dt: float) -> None:
        if not unit.alive:
            return
        target = self._nearest_enemy_ahead(unit)
        edge_distance = abs((C.LANE_RIGHT if unit.faction == "mordor" else C.LANE_LEFT) - unit.x)
        if target and abs(target.x - unit.x) <= unit.kind.attack_range + target.kind.size:
            if unit.attack_timer <= 0:
                self._attack(unit, target)
        elif edge_distance <= unit.kind.attack_range + 22:
            if unit.attack_timer <= 0:
                self._attack_base(unit)
        elif not self._blocked_by_ally(unit):
            unit.x += unit.direction * unit.kind.speed * dt
            unit.x = max(C.LANE_LEFT, min(C.LANE_RIGHT, unit.x))

    def _attack(self, attacker: Unit, target: Unit) -> None:
        attacker.attack_timer = attacker.kind.attack_cooldown
        self.events.append(CombatEvent("attack", attacker.x, attacker.faction))
        if attacker.kind.ranged:
            self.projectiles.append(Projectile(attacker.faction, attacker.x, target.id,
                                               attacker.kind.damage, attacker.kind.projectile_speed))
        else:
            self._damage_unit(target, attacker.kind.damage)

    def _attack_base(self, attacker: Unit) -> None:
        attacker.attack_timer = attacker.kind.attack_cooldown
        defender = self.gondor if attacker.faction == "mordor" else self.mordor
        defender.base_health = max(0.0, defender.base_health - attacker.kind.damage)
        self.events.append(CombatEvent("base_hit", attacker.x, attacker.faction, attacker.kind.damage))

    def _damage_unit(self, target: Unit, damage: float) -> None:
        if not target.alive:
            return
        target.health = max(0.0, float(target.health) - damage)
        target.flash_timer = 0.12
        self.events.append(CombatEvent("hit", target.x, target.faction, damage))

    def _update_projectiles(self, dt: float) -> None:
        by_id = {u.id: u for u in self.units if u.alive}
        for projectile in self.projectiles:
            target = by_id.get(projectile.target_id)
            if not target:
                projectile.dead = True
                continue
            delta = target.x - projectile.x
            travel = projectile.speed * dt
            if abs(delta) <= travel + target.kind.size:
                self._damage_unit(target, projectile.damage)
                projectile.dead = True
            else:
                projectile.x += travel if delta > 0 else -travel
        self.projectiles = [p for p in self.projectiles if not p.dead]

    def _update_towers(self, dt: float) -> None:
        for army, tower_x, enemy_faction in (
            (self.mordor, C.LANE_LEFT, "gondor"),
            (self.gondor, C.LANE_RIGHT, "mordor"),
        ):
            army.tower_timer = max(0.0, army.tower_timer - dt)
            targets = [u for u in self.units if u.faction == enemy_faction
                       and u.alive and abs(u.x - tower_x) <= C.BASE_ATTACK_RANGE]
            if targets and army.tower_timer <= 0:
                target = min(targets, key=lambda u: abs(u.x - tower_x))
                self.projectiles.append(Projectile(army.faction, tower_x, target.id,
                                                   C.BASE_ATTACK_DAMAGE, 390))
                army.tower_timer = C.BASE_ATTACK_COOLDOWN
                self.events.append(CombatEvent("tower", tower_x, army.faction))

    def _remove_dead(self) -> None:
        survivors = []
        for unit in self.units:
            if unit.alive:
                survivors.append(unit)
                continue
            victor = self.gondor if unit.faction == "mordor" else self.mordor
            victor.gold += unit.kind.bounty
            self.events.append(CombatEvent("death", unit.x, unit.faction, unit.kind.bounty))
        self.units = survivors

    def _update_siege_pressure(self, dt: float) -> None:
        """Resolve late stalemates by rewarding control of enemy territory."""
        if self.elapsed < C.SIEGE_PRESSURE_START:
            return
        midpoint = (C.LANE_LEFT + C.LANE_RIGHT) / 2
        mordor_pressure = sum(u.x > midpoint for u in self.units if u.faction == "mordor")
        gondor_pressure = sum(u.x < midpoint for u in self.units if u.faction == "gondor")
        advantage = mordor_pressure - gondor_pressure
        if advantage > 0:
            self.gondor.base_health = max(
                0.0, self.gondor.base_health - advantage * C.SIEGE_PRESSURE_DAMAGE * dt
            )
        elif advantage < 0:
            self.mordor.base_health = max(
                0.0, self.mordor.base_health + advantage * C.SIEGE_PRESSURE_DAMAGE * dt
            )

    def _check_game_over(self) -> None:
        if self.gondor.base_health <= 0:
            self.state = "victory"
            self.message = "Gondor has fallen"
        elif self.mordor.base_health <= 0:
            self.state = "defeat"
            self.message = "The Black Gate has fallen"