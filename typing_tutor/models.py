"""Small data objects shared by the game rules and the interface."""

from dataclasses import dataclass
from enum import Enum


class GameState(Enum):
    READY = "ready"
    PLAYING = "playing"
    FINISHED = "finished"
    STOPPED = "stopped"


@dataclass
class FallingCharacter:
    identifier: int
    value: str
    x: float  # Position from 0 (left) to 1 (right).
    y: float  # Position from 0 (top) to 1 (bottom).
    speed: float  # Fraction of the play area traveled per second.


@dataclass
class GameStats:
    hits: int = 0
    misses: int = 0
    key_presses: int = 0

    @property
    def accuracy(self) -> float:
        """Correct matches divided by gameplay key presses."""
        if self.key_presses == 0:
            return 0.0
        return 100.0 * self.hits / self.key_presses
