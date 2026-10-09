# Implementa as regras do ambiente, transições de estado, sucessores e heurística relaxada.
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
    if destination not in level.graph[state.position]:
        raise ValueError(
            f"Movimento inválido: {state.position} -> {destination} não é uma aresta."
        )

    active_guards = state.active_guards
    moving_states = list(state.moving_guards)

    if destination in active_guards:
        if level.guards[destination] == state.position:
            return None
        active_guards = frozenset(
            guard for guard in active_guards if guard != destination
        )

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

    if watched_by_static_guard(level, after_agent, destination):
        return None

    if destination not in level.hiding_nodes:
        for index, guard_state in enumerate(after_agent.moving_guards):
            if not guard_state.active:
                continue
            if _moving_guard_front(level, index, guard_state) == destination:
                return None

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

    for index, guard_state in enumerate(next_state.moving_guards):
        if not guard_state.active:
            continue
        if (
            _moving_guard_position(level, index, guard_state) == destination
            and destination not in level.hiding_nodes
        ):
            return None

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
    to_goal = relaxed_distances(level, level.goal)

    if require_briefcase and level.briefcase and not state.briefcase_collected:
        to_briefcase = relaxed_distances(level, level.briefcase)
        return to_briefcase[state.position] + to_goal[level.briefcase]

    return to_goal[state.position]
