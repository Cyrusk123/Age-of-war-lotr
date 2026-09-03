import unittest

from lotr_war import config as C
from lotr_war.simulation import GameSimulation


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.game = GameSimulation(enable_ai=False)

    def advance(self, seconds, step=1 / 60):
        for _ in range(int(seconds / step)):
            self.game.update(step)

    def test_melee_units_attack_and_award_bounty(self):
        attacker = self.game.spawn("uruk", 500)
        victim = self.game.spawn("soldier", 525)
        victim.health = 1
        gold = self.game.mordor.gold
        self.game.update(0.05)
        self.assertNotIn(victim, self.game.units)
        self.assertEqual(self.game.mordor.gold, gold + victim.kind.bounty + C.PASSIVE_INCOME * 0.05)
        self.assertGreater(attacker.attack_timer, 0)

    def test_ranged_attack_creates_projectile_and_deals_damage(self):
        archer = self.game.spawn("orc_archer", 400)
        target = self.game.spawn("soldier", 520)
        starting_health = target.health
        self.game.update(0.02)
        self.assertEqual(len(self.game.projectiles), 1)
        self.advance(0.6)
        self.assertLess(target.health, starting_health)
        self.assertGreater(archer.attack_timer, 0)

    def test_unit_at_enemy_edge_damages_base(self):
        unit = self.game.spawn("uruk", C.LANE_RIGHT - 20)
        health = self.game.gondor.base_health
        self.game.update(0.02)
        self.assertEqual(self.game.gondor.base_health, health - unit.kind.damage)

    def test_destroying_base_causes_victory(self):
        self.game.gondor.base_health = 1
        self.game.spawn("orc", C.LANE_RIGHT - 10)
        self.game.update(0.05)
        self.assertEqual(self.game.state, "victory")

    def test_tower_fires_at_enemy_in_range(self):
        target = self.game.spawn("soldier", C.LANE_LEFT + 100)
        health = target.health
        self.game.update(0.02)
        self.assertTrue(self.game.projectiles)
        self.advance(0.5)
        self.assertLess(target.health, health)

    def test_allies_do_not_stack_while_walking(self):
        front = self.game.spawn("orc", 300)
        rear = self.game.spawn("orc", 270)
        rear_start = rear.x
        self.game.update(0.1)
        self.assertGreater(front.x, 300)
        self.assertEqual(rear.x, rear_start)

    def test_late_siege_pressure_rewards_enemy_territory_control(self):
        self.game.elapsed = C.SIEGE_PRESSURE_START
        self.game.spawn("orc", 800)
        health = self.game.gondor.base_health
        self.game.update(1.0)
        self.assertLess(self.game.gondor.base_health, health)


if __name__ == "__main__":
    unittest.main()