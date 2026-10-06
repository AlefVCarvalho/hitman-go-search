from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, FrozenSet


@dataclass(frozen=True, slots=True)
class State:
    position: str
    active_guards: FrozenSet[str]


@dataclass(frozen=True, slots=True)
class Level:
    name: str
    graph: Mapping[str, tuple[str, ...]]
    start: str
    goal: str
    guards: FrozenSet[str]

    def initial_state(self) -> State:
        return State(self.start, self.guards)
