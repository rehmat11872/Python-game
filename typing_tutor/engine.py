"""Pure game rules. This module does not depend on Tkinter."""

from __future__ import annotations

import random
import string
from collections import deque
from dataclasses import dataclass

from .models import FallingCharacter, GameState, GameStats

CHARACTERS = string.ascii_lowercase + string.ascii_uppercase + string.digits


@dataclass(frozen=True)
class GameSettings:
    duration_seconds: int = 60
    spawn_interval_seconds: float = 1.35
    fall_speed: float = 0.155
    dead_bar_y: float = 0.84
    maximum_active: int = 10
    upcoming_count: int = 8

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0 or self.spawn_interval_seconds <= 0:
            raise ValueError("Duration and spawn interval must be positive")
        if self.fall_speed <= 0 or not 0 < self.dead_bar_y < 1:
            raise ValueError("Fall speed and Dead Bar position must be valid")
        if self.maximum_active <= 0 or self.upcoming_count <= 0:
            raise ValueError("Character limits must be positive")


class GameEngine:
    """Manage character generation, movement, matching, and score."""

    def __init__(
        self,
        settings: GameSettings | None = None,
        random_source: random.Random | None = None,
    ) -> None:
        self.settings = settings or GameSettings()
        self.random = random_source or random.Random()
        self.state = GameState.READY
        self.stats = GameStats()
        self.active: list[FallingCharacter] = []
        self.upcoming: deque[str] = deque()
        self.time_left = float(self.settings.duration_seconds)
        self._spawn_elapsed = 0.0
        self._next_identifier = 1

    def start(self) -> None:
        """Start a fresh session, discarding any previous session."""
        self.state = GameState.PLAYING
        self.stats = GameStats()
        self.active = []
        self.upcoming = deque()
        self.time_left = float(self.settings.duration_seconds)
        self._spawn_elapsed = 0.0
        self._next_identifier = 1
        self._fill_upcoming()
        self._spawn_character()

    def _fill_upcoming(self) -> None:
        while len(self.upcoming) < self.settings.upcoming_count:
            self.upcoming.append(self.random.choice(CHARACTERS))

    def _spawn_character(self) -> None:
        if len(self.active) >= self.settings.maximum_active:
            return
        value = self.upcoming.popleft()
        self._fill_upcoming()
        self.active.append(
            FallingCharacter(
                identifier=self._next_identifier,
                value=value,
                x=self.random.uniform(0.09, 0.91),
                y=-0.035,
                speed=self.settings.fall_speed,
            )
        )
        self._next_identifier += 1

    def update(self, seconds: float) -> None:
        """Advance game time; the UI calls this once per animation frame."""
        if self.state != GameState.PLAYING:
            return
        if seconds < 0:
            raise ValueError("Elapsed time cannot be negative")

        remaining_step = min(seconds, self.time_left)
        while remaining_step > 0:
            until_spawn = self.settings.spawn_interval_seconds - self._spawn_elapsed
            step = min(remaining_step, until_spawn)
            for character in self.active:
                character.y += character.speed * step

            self.time_left -= step
            remaining_step -= step
            self._spawn_elapsed += step
            self.active = [
                character for character in self.active if not self._count_miss(character)
            ]

            if self._spawn_elapsed >= self.settings.spawn_interval_seconds - 1e-9:
                self._spawn_elapsed = 0.0
                if self.time_left > 0:
                    self._spawn_character()

        if self.time_left <= 0:
            self.time_left = 0.0
            self.state = GameState.FINISHED

    def _count_miss(self, character: FallingCharacter) -> bool:
        if character.y < self.settings.dead_bar_y:
            return False
        self.stats.misses += 1
        return True

    def press(self, key: str) -> bool:
        """Match the lowest falling copy of a key; return whether it hit."""
        if self.state != GameState.PLAYING or len(key) != 1 or not key.isprintable():
            return False

        self.stats.key_presses += 1
        # Sorting gives priority to the character closest to the Dead Bar.
        # The following loop is a linear search through that ordered list.
        for character in sorted(self.active, key=lambda item: -item.y):
            if character.value == key:
                self.active.remove(character)
                self.stats.hits += 1
                return True
        return False

    def stop(self) -> None:
        """End the current game when the player presses Escape."""
        if self.state == GameState.PLAYING:
            self.state = GameState.STOPPED
