from __future__ import annotations

from collections import deque
from typing import Iterable

from .models import Level, MovingGuardState, State


def is_goal(level: Level, state: State) -> bool:
    if state.position != level.goal:
        return False
    if level.briefcase_required and not state.has_briefcase:
        return False
    return True


def moving_guard_position(level: Level, guard_index: int, state: State) -> str | None:
    guard_state = state.moving_guards[guard_index]
    if not guard_state.active:
        return None
    return level.moving_guards[guard_index].route[guard_state.index]


def moving_guard_watch_node(
    level: Level,
    guard_index: int,
    state: State,
) -> str | None:
    """Nó observado pelo guarda móvel conforme a direção atual da patrulha."""
    guard_state = state.moving_guards[guard_index]
    if not guard_state.active:
        return None

    route = level.moving_guards[guard_index].route
    next_index = guard_state.index + guard_state.direction

    # Nos extremos, o guarda se vira e passa a observar o caminho de volta.
    if next_index < 0 or next_index >= len(route):
        next_index = guard_state.index - guard_state.direction

    if 0 <= next_index < len(route):
        return route[next_index]
    return None


def watched_by_guard(level: Level, state: State, node: str) -> bool:
    # Guardas estáticos: o valor do dicionário indica o nó observado.
    if any(
        level.guards[guard_position] == node
        for guard_position in state.active_guards
    ):
        return True

    # Guardas móveis: observam o próximo nó no sentido atual da patrulha.
    return any(
        moving_guard_watch_node(level, i, state) == node
        for i in range(len(state.moving_guards))
    )


def _remove_moving_guard_at_destination(
    level: Level,
    state: State,
    destination: str,
) -> tuple[MovingGuardState, ...]:
    states = list(state.moving_guards)

    for i, guard_state in enumerate(states):
        if not guard_state.active:
            continue
        if moving_guard_position(level, i, state) == destination:
            states[i] = MovingGuardState(
                index=guard_state.index,
                direction=guard_state.direction,
                active=False,
            )

    return tuple(states)


def _advance_moving_guards(level: Level, state: State) -> State | None:
    """Avança cada guarda móvel em um passo após a ação do agente."""
    next_guards: list[MovingGuardState] = []

    for i, guard_state in enumerate(state.moving_guards):
        if not guard_state.active:
            next_guards.append(guard_state)
            continue

        route = level.moving_guards[i].route
        direction = guard_state.direction
        next_index = guard_state.index + direction

        if next_index < 0 or next_index >= len(route):
            direction *= -1
            next_index = guard_state.index + direction

        # Uma rota com apenas um nó representa um guarda imóvel.
        if next_index < 0 or next_index >= len(route):
            next_index = guard_state.index

        # Ao chegar a uma extremidade, já fica orientado para o caminho de volta.
        if next_index == 0:
            direction = 1
        elif next_index == len(route) - 1:
            direction = -1

        # Se o guarda entra no nó ocupado pelo agente, o estado é de derrota.
        if route[next_index] == state.position:
            return None

        next_guards.append(
            MovingGuardState(
                index=next_index,
                direction=direction,
                active=True,
            )
        )

    return State(
        position=state.position,
        active_guards=state.active_guards,
        moving_guards=tuple(next_guards),
        has_briefcase=state.has_briefcase,
    )


def apply_move(level: Level, state: State, destination: str) -> State | None:
    if destination not in level.graph[state.position]:
        raise ValueError(
            f"Movimento inválido: {state.position} -> {destination} não é uma aresta."
        )

    active_guards = state.active_guards

    # Mantém a regra já usada no projeto: entrar no nó ocupado por um guarda
    # estático elimina esse guarda.
    if destination in active_guards:
        active_guards = frozenset(
            guard for guard in active_guards if guard != destination
        )

    # O mesmo princípio é aplicado aos guardas móveis no exemplo inicial.
    moving_guards = _remove_moving_guard_at_destination(level, state, destination)

    has_briefcase = state.has_briefcase or (destination == level.briefcase)

    next_state = State(
        position=destination,
        active_guards=active_guards,
        moving_guards=moving_guards,
        has_briefcase=has_briefcase,
    )

    # Primeiro verifica se o agente terminou o próprio movimento em uma área
    # observada por algum guarda ainda ativo.
    if watched_by_guard(level, next_state, destination):
        return None

    # Em seguida os guardas móveis avançam um passo.
    next_state = _advance_moving_guards(level, next_state)
    if next_state is None:
        return None

    return next_state


def successors(level: Level, state: State) -> Iterable[tuple[str, State, int]]:
    for destination in level.graph[state.position]:
        next_state = apply_move(level, state, destination)
        if next_state is None:
            continue
        yield destination, next_state, 1


def _distances_from(level: Level, start: str) -> dict[str, int]:
    distance = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in level.graph[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    return distance


def relaxed_distances_to_goal(level: Level) -> dict[str, int]:
    return _distances_from(level, level.goal)


def heuristic_cost(level: Level, state: State) -> int:
    """Heurística relaxada para fases com ou sem maleta.

    Sem maleta pendente: distância mínima da posição atual até a saída.
    Com maleta pendente: posição -> maleta + maleta -> saída.

    Guardas são ignorados, portanto a estimativa não adiciona desvios causados
    pelos inimigos.
    """
    to_goal = _distances_from(level, level.goal)

    if not level.briefcase_required or state.has_briefcase or level.briefcase is None:
        return to_goal.get(state.position, 0)

    from_briefcase = _distances_from(level, level.briefcase)
    return (
        from_briefcase.get(state.position, 0)
        + to_goal.get(level.briefcase, 0)
    )
