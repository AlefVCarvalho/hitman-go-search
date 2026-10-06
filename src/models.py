from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping


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
    guards: Mapping[str, str]

    def initial_state(self) -> State:
        return State(self.start, frozenset(self.guards))