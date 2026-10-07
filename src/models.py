from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping


@dataclass(frozen=True, slots=True)
class MovingGuard:
    """Configuração fixa de um guarda que patrulha uma rota linear."""

    name: str
    route: tuple[str, ...]
    start_index: int
    start_direction: int = 1


@dataclass(frozen=True, slots=True)
class MovingGuardState:
    """Parte variável de um guarda móvel dentro de um estado de busca."""

    index: int
    direction: int
    active: bool = True


@dataclass(frozen=True, slots=True)
class State:
    position: str
    active_guards: FrozenSet[str]
    moving_guards: tuple[MovingGuardState, ...] = ()
    briefcase_collected: bool = False


@dataclass(frozen=True, slots=True)
class Level:
    name: str
    graph: Mapping[str, tuple[str, ...]]
    start: str
    goal: str
    guards: Mapping[str, str | None]
    moving_guards: tuple[MovingGuard, ...] = ()
    hiding_nodes: FrozenSet[str] = frozenset()
    briefcase: str | None = None

    def initial_state(self) -> State:
        moving_state = tuple(
            MovingGuardState(
                index=guard.start_index,
                direction=guard.start_direction,
                active=True,
            )
            for guard in self.moving_guards
        )
        return State(
            position=self.start,
            active_guards=frozenset(self.guards),
            moving_guards=moving_state,
            briefcase_collected=self.start == self.briefcase,
        )
