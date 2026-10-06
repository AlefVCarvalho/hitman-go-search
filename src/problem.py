from __future__ import annotations

from collections import deque
from typing import Iterable

from .models import Level, State


def is_goal(level: Level, state: State) -> bool:
    return state.position == level.goal


def watched_by_guard(level: Level, state: State, node: str) -> bool:
    return any(
        level.guards[guard_position] == node
        for guard_position in state.active_guards
    )


def apply_move(level: Level, state: State, destination: str) -> State | None:
    if destination not in level.graph[state.position]:
        raise ValueError(
            f"Movimento inválido: {state.position} -> {destination} não é uma aresta."
        )

    active_guards = state.active_guards

    if destination in active_guards:
        active_guards = frozenset(
            guard for guard in active_guards if guard != destination
        )

    next_state = State(destination, active_guards)

    if watched_by_guard(level, next_state, destination):
        return None

    return next_state


def successors(level: Level, state: State) -> Iterable[tuple[str, State, int]]:
    for destination in level.graph[state.position]:
        next_state = apply_move(level, state, destination)
        if next_state is None:
            continue
        yield destination, next_state, 1


def relaxed_distances_to_goal(level: Level) -> dict[str, int]:
    distance = {level.goal: 0}
    queue = deque([level.goal])

    while queue:
        current = queue.popleft()
        for neighbor in level.graph[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    return distance