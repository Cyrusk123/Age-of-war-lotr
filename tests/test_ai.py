import unittest

from lotr_war.ai import GondorAI
from lotr_war.simulation import GameSimulation


class GondorAITests(unittest.TestCase):
    def setUp(self):
        self.game = GameSimulation(enable_ai=False)
        self.ai = GondorAI(seed=2)

    def test_ai_prioritizes_a_frontline_when_it_has_none(self):
        self.game.spawn("gondor_archer", 900)
        self.assertEqual(self.ai.choose_unit(self.game), "soldier")

    def test_ai_uses_heavy_defender_under_pressure(self):
        self.game.gondor.gold = 500
        self.assertEqual(self.ai.choose_unit(self.game, pressure=4), "tower_guard")

    def test_ai_respects_economy(self):
        self.game.gondor.gold = 0
        self.assertFalse(self.ai.try_recruit(self.game, pressure=4))
        self.assertEqual(self.game.population("gondor"), 0)

    def test_ai_spawns_valid_unit_immediately(self):
        self.game.gondor.gold = 500
        self.assertTrue(self.ai.try_recruit(self.game))
        self.assertEqual(self.game.population("gondor"), 1)
        self.assertEqual(self.game.units[0].kind.faction, "gondor")


if __name__ == "__main__":
    unittest.main()