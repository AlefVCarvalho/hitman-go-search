# modelos usados para guardar as informações do jogo
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping


# Guarda informações fixas de um guarda
@dataclass(frozen=True, slots=True)
class MovingGuard:
    name: str
    route: tuple[str, ...]
    start_index: int
    start_direction: int = 1


# Guarda situação do guarda móvel em um momento da partida
@dataclass(frozen=True, slots=True)
class MovingGuardState:
    index: int
    direction: int
    active: bool = True


# Representa uma situação completa do jogo durante a busca
# posição do agente, quais inimigos continuam ativos e se a maleta já foi coletada
@dataclass(frozen=True, slots=True)
class State:
    position: str
    active_guards: FrozenSet[str]
    moving_guards: tuple[MovingGuardState, ...] = ()
    briefcase_collected: bool = False


# Reúne tudo da fase: mapa, início, saída, guardas, arbustos e posição da maleta (quando ela existe)
# O mapa mostra quais nós estão ligados entre si
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

    # Monta a situação inicial da fase antes de começar a busca
    # Guardas moveis
    def initial_state(self) -> State:
        moving_state = tuple(
            MovingGuardState(
                index=guard.start_index,
                direction=guard.start_direction,
                active=True,
            )
            for guard in self.moving_guards
        )
        # Agente no início, guardas estáticos ativos e maleta como coletada se ela estiver no nó
        return State(
            position=self.start,
            active_guards=frozenset(self.guards),
            moving_guards=moving_state,
            briefcase_collected=self.start == self.briefcase,
        )
