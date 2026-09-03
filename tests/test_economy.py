import unittest

from lotr_war import config as C
from lotr_war.simulation import GameSimulation


class EconomyTests(unittest.TestCase):
    def setUp(self):
        self.game = GameSimulation(enable_ai=False)

    def test_recruitment_spends_gold_and_enters_queue(self):
        self.assertTrue(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.mordor.gold, C.STARTING_GOLD - 60)
        self.assertEqual(self.game.mordor.queue[0].kind.key, "orc")

    def test_training_completes_and_spawns_at_mordor_base(self):
        self.game.recruit("mordor", "orc")
        for _ in range(72):
            self.game.update(1 / 60)
        self.assertEqual(len(self.game.mordor.queue), 0)
        self.assertEqual(len(self.game.units), 1)
        self.assertGreaterEqual(self.game.units[0].x, C.LANE_LEFT)
        self.assertLess(self.game.units[0].x, C.LANE_LEFT + 5)

    def test_cannot_buy_enemy_or_unaffordable_unit(self):
        self.assertFalse(self.game.recruit("mordor", "soldier"))
        self.game.mordor.gold = 0
        self.assertFalse(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.message, "Not enough gold")

    def test_population_includes_queued_units(self):
        self.game.mordor.gold = 10_000
        for _ in range(C.MAX_QUEUE):
            self.assertTrue(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.population("mordor"), C.MAX_QUEUE)
        self.assertFalse(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.message, "Recruitment queue full")

    def test_income_is_frame_rate_independent(self):
        game_a = GameSimulation(enable_ai=False)
        game_b = GameSimulation(enable_ai=False)
        game_a.update(0.2)
        for _ in range(4):
            game_b.update(0.05)
        self.assertAlmostEqual(game_a.mordor.gold, game_b.mordor.gold, places=5)


if __name__ == "__main__":
    unittest.main()