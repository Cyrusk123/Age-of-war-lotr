import unittest

from lotr_war import config as C
from lotr_war.simulation import GameSimulation


class EconomyTests(unittest.TestCase):
    def setUp(self):
        self.game = GameSimulation(enable_ai=False)

    def test_recruitment_spends_gold_and_spawns_immediately(self):
        self.assertTrue(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.mordor.gold, C.STARTING_GOLD - 60)
        self.assertEqual(len(self.game.units), 1)
        self.assertEqual(self.game.units[0].kind.key, "orc")
        self.assertEqual(self.game.units[0].x, C.LANE_LEFT)

    def test_cannot_buy_enemy_or_unaffordable_unit(self):
        self.assertFalse(self.game.recruit("mordor", "soldier"))
        self.game.mordor.gold = 0
        self.assertFalse(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.message, "Not enough gold")

    def test_population_cap_blocks_further_instant_spawns(self):
        self.game.mordor.gold = 10_000
        for _ in range(C.POPULATION_CAP):
            self.assertTrue(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.population("mordor"), C.POPULATION_CAP)
        self.assertFalse(self.game.recruit("mordor", "orc"))
        self.assertEqual(self.game.message, "Population limit reached")

    def test_income_is_frame_rate_independent(self):
        game_a = GameSimulation(enable_ai=False)
        game_b = GameSimulation(enable_ai=False)
        game_a.update(0.2)
        for _ in range(4):
            game_b.update(0.05)
        self.assertAlmostEqual(game_a.mordor.gold, game_b.mordor.gold, places=5)

    def test_first_era_rosters_have_five_units_and_one_hero(self):
        self.assertEqual(len(C.MORDOR_UNITS), 5)
        self.assertEqual(len(C.GONDOR_UNITS), 5)
        self.assertEqual([hero.name for hero in C.MORDOR_HEROES], ["Lurtz"])
        self.assertEqual([hero.name for hero in C.GONDOR_HEROES], ["Boromir"])
        self.assertTrue(all(hero.era == 1 and hero.is_hero
                            for hero in C.MORDOR_HEROES + C.GONDOR_HEROES))

    def test_only_one_copy_of_a_hero_can_be_alive(self):
        self.game.mordor.gold = 1_000
        self.assertTrue(self.game.recruit("mordor", "lurtz"))
        self.assertFalse(self.game.recruit("mordor", "lurtz"))
        self.assertEqual(self.game.message, "Lurtz is already deployed")
        self.game.units[0].health = 0
        self.game.update(0.01)
        self.assertTrue(self.game.recruit("mordor", "lurtz"))


if __name__ == "__main__":
    unittest.main()