"""Offline tests for the rules; no window or third-party package is needed."""

import random
import unittest

from typing_tutor.engine import CHARACTERS, GameEngine, GameSettings
from typing_tutor.models import FallingCharacter, GameState


class GameEngineTests(unittest.TestCase):
    def make_game(self, **options):
        game = GameEngine(GameSettings(**options), random.Random(7))
        game.start()
        return game

    def test_generated_pool_contains_all_required_character_groups(self):
        self.assertEqual(len(CHARACTERS), 62)
        self.assertIn("a", CHARACTERS)
        self.assertIn("Z", CHARACTERS)
        self.assertIn("9", CHARACTERS)

    def test_start_creates_character_and_queue(self):
        game = self.make_game()
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertEqual(len(game.active), 1)
        self.assertEqual(len(game.upcoming), game.settings.upcoming_count)
        self.assertEqual(game.time_left, 60)

    def test_matching_is_case_sensitive_and_updates_accuracy(self):
        game = self.make_game()
        game.active[0].value = "A"
        self.assertFalse(game.press("a"))
        self.assertTrue(game.press("A"))
        self.assertEqual(game.stats.key_presses, 2)
        self.assertEqual(game.stats.hits, 1)
        self.assertEqual(game.stats.accuracy, 50.0)
        self.assertEqual(len(game.active), 0)

    def test_same_letter_matches_character_nearest_dead_bar(self):
        game = self.make_game()
        game.active = [
            FallingCharacter(1, "x", 0.3, 0.2, 0.1),
            FallingCharacter(2, "x", 0.6, 0.7, 0.1),
        ]
        self.assertTrue(game.press("x"))
        self.assertEqual([item.identifier for item in game.active], [1])

    def test_character_crossing_bar_counts_one_miss(self):
        game = self.make_game(spawn_interval_seconds=100)
        game.update(6)
        self.assertEqual(game.stats.misses, 1)
        self.assertEqual(len(game.active), 0)
        game.update(1)
        self.assertEqual(game.stats.misses, 1)

    def test_queue_spawns_over_time_and_keeps_a_fixed_lookahead(self):
        game = self.make_game(spawn_interval_seconds=1, fall_speed=0.01)
        game.update(2.5)
        self.assertEqual(len(game.active), 3)
        self.assertEqual(len(game.upcoming), 8)

    def test_timer_ends_game_and_escape_stops_early(self):
        game = self.make_game()
        game.update(60)
        self.assertEqual(game.state, GameState.FINISHED)
        self.assertEqual(game.time_left, 0)
        self.assertFalse(game.press("a"))
        game.start()
        game.stop()
        self.assertEqual(game.state, GameState.STOPPED)
        self.assertEqual(game.stats.key_presses, 0)

    def test_restart_resets_statistics_and_characters(self):
        game = self.make_game()
        game.press("?")
        game.update(2)
        game.start()
        self.assertEqual(game.stats.key_presses, 0)
        self.assertEqual(game.stats.misses, 0)
        self.assertEqual(len(game.active), 1)


if __name__ == "__main__":
    unittest.main()
