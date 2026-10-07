from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping


@dataclass(frozen=True, slots=True)
class MovingGuard:
    """Configuração fixa de um guarda que patrulha uma rota linear."""

    route: tuple[str, ...]
    start_index: int = 0
    start_direction: int = 1


@dataclass(frozen=True, slots=True)
class MovingGuardState:
    """Parte dinâmica de um guarda móvel armazenada no estado de busca."""

    index: int
    direction: int
    active: bool = True


@dataclass(frozen=True, slots=True)
class State:
    position: str
    active_guards: FrozenSet[str]
    moving_guards: tuple[MovingGuardState, ...] = ()
    has_briefcase: bool = False


@dataclass(frozen=True, slots=True)
class Level:
    name: str
    graph: Mapping[str, tuple[str, ...]]
    start: str
    goal: str
    guards: Mapping[str, str]
    moving_guards: tuple[MovingGuard, ...] = ()
    briefcase: str | None = None
    briefcase_required: bool = False

    def initial_state(self) -> State:
        moving_states = tuple(
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
            moving_guards=moving_states,
            has_briefcase=(self.briefcase == self.start),
        )
