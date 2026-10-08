from __future__ import annotations

from collections import deque
from functools import lru_cache
from typing import Iterable

from .models import Level, MovingGuardState, State


def is_goal(level: Level, state: State, require_briefcase: bool = False) -> bool:
    if state.position != level.goal:
        return False
    if require_briefcase:
        return state.briefcase_collected
    return True


def watched_by_static_guard(level: Level, state: State, node: str) -> bool:
    if node in level.hiding_nodes:
        return False
    return any(
        level.guards[guard_position] is not None
        and level.guards[guard_position] == node
        for guard_position in state.active_guards
    )


def _moving_guard_position(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> str:
    return level.moving_guards[guard_index].route[guard_state.index]


def _moving_guard_front(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> str | None:
    """Retorna o nó para o qual o guarda está olhando neste instante.

    Nas extremidades da rota, a direção é interpretada como já invertida: o
    guarda não consome um turno parado apenas para virar.
    """
    guard = level.moving_guards[guard_index]
    if len(guard.route) <= 1:
        return None

    direction = guard_state.direction
    next_index = guard_state.index + direction
    if not 0 <= next_index < len(guard.route):
        direction *= -1
        next_index = guard_state.index + direction

    return guard.route[next_index]


def _advance_moving_guard(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> MovingGuardState:
    """Move um guarda uma casa, invertendo imediatamente nas extremidades."""
    if not guard_state.active:
        return guard_state

    guard = level.moving_guards[guard_index]
    if len(guard.route) <= 1:
        return guard_state

    direction = guard_state.direction
    next_index = guard_state.index + direction

    if not 0 <= next_index < len(guard.route):
        direction *= -1
        next_index = guard_state.index + direction

    return MovingGuardState(index=next_index, direction=direction, active=True)


def apply_move(level: Level, state: State, destination: str) -> State | None:
    """Aplica um turno completo de forma determinística.

    Ordem de um turno:
    1. o agente se move;
    2. resolve-se a interação imediata com guardas no destino e a visão dos
       guardas estáticos;
    3. guardas amarelos ativos avançam uma casa;
    4. resolve-se colisão e campo de visão após o movimento dos amarelos.

    Regras usadas no modelo:
    - cada ação do agente custa 1 turno;
    - atacar um guarda pela frente resulta em derrota;
    - entrar lateralmente ou por trás elimina o guarda;
    - guardas amarelos movem uma casa por turno;
    - ao chegar ao extremo da rota, invertem a direção e já se deslocam no
      turno seguinte, sem gastar um turno apenas para virar;
    - arbustos impedem detecção e permitem que guardas atravessem o nó sem
      detectar o agente escondido;
    - a maleta é coletada automaticamente ao visitar seu nó.
    """
    if destination not in level.graph[state.position]:
        raise ValueError(
            f"Movimento inválido: {state.position} -> {destination} não é uma aresta."
        )

    active_guards = state.active_guards
    moving_states = list(state.moving_guards)

    # 1) O agente se move primeiro.
    # Interação com guarda azul no nó de destino.
    if destination in active_guards:
        if level.guards[destination] == state.position:
            return None
        active_guards = frozenset(
            guard for guard in active_guards if guard != destination
        )

    # Interação com guarda amarelo ainda em sua posição anterior ao movimento.
    for index, guard_state in enumerate(moving_states):
        if not guard_state.active:
            continue
        if _moving_guard_position(level, index, guard_state) != destination:
            continue

        if _moving_guard_front(level, index, guard_state) == state.position:
            return None

        moving_states[index] = MovingGuardState(
            index=guard_state.index,
            direction=guard_state.direction,
            active=False,
        )

    briefcase_collected = state.briefcase_collected or destination == level.briefcase

    after_agent = State(
        position=destination,
        active_guards=active_guards,
        moving_guards=tuple(moving_states),
        briefcase_collected=briefcase_collected,
    )

    # Um guarda azul pode vigiar o nó alcançado pelo agente.
    if watched_by_static_guard(level, after_agent, destination):
        return None

    # Antes de se moverem, guardas amarelos ainda ativos também podem estar
    # olhando diretamente para o agente. Arbustos bloqueiam essa detecção.
    if destination not in level.hiding_nodes:
        for index, guard_state in enumerate(after_agent.moving_guards):
            if not guard_state.active:
                continue
            if _moving_guard_front(level, index, guard_state) == destination:
                return None

    # 2) Depois da ação do jogador, os guardas amarelos avançam.
    advanced_states = tuple(
        _advance_moving_guard(level, index, guard_state)
        for index, guard_state in enumerate(after_agent.moving_guards)
    )

    next_state = State(
        position=destination,
        active_guards=active_guards,
        moving_guards=advanced_states,
        briefcase_collected=briefcase_collected,
    )

    # Fora de um arbusto, um guarda que termina no mesmo nó captura o agente.
    for index, guard_state in enumerate(next_state.moving_guards):
        if not guard_state.active:
            continue
        if (
            _moving_guard_position(level, index, guard_state) == destination
            and destination not in level.hiding_nodes
        ):
            return None

    # Após andar, um guarda pode terminar olhando para o agente.
    if destination not in level.hiding_nodes:
        for index, guard_state in enumerate(next_state.moving_guards):
            if not guard_state.active:
                continue
            if _moving_guard_front(level, index, guard_state) == destination:
                return None

    return next_state


def successors(level: Level, state: State) -> Iterable[tuple[str, State, int]]:
    for destination in level.graph[state.position]:
        next_state = apply_move(level, state, destination)
        if next_state is None:
            continue
        yield destination, next_state, 1


@lru_cache(maxsize=None)
def _distances_from(
    graph_items: tuple[tuple[str, tuple[str, ...]], ...],
    source: str,
) -> dict[str, int]:
    graph = dict(graph_items)
    distance = {source: 0}
    queue = deque([source])

    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    return distance


def relaxed_distances(level: Level, source: str) -> dict[str, int]:
    graph_items = tuple(
        sorted((node, tuple(neighbors)) for node, neighbors in level.graph.items())
    )
    return _distances_from(graph_items, source)


def relaxed_heuristic(
    level: Level,
    state: State,
    require_briefcase: bool = False,
) -> int:
    """Menor distância no grafo ignorando todos os guardas.

    Quando a maleta é obrigatória e ainda não foi coletada, soma:
        posição -> maleta + maleta -> objetivo.
    """
    to_goal = relaxed_distances(level, level.goal)

    if require_briefcase and level.briefcase and not state.briefcase_collected:
        to_briefcase = relaxed_distances(level, level.briefcase)
        return to_briefcase[state.position] + to_goal[level.briefcase]

    return to_goal[state.position]
