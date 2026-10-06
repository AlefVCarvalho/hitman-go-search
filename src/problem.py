from __future__ import annotations

from collections import deque
from typing import Iterable

from .models import Level, State


def is_goal(level: Level, state: State) -> bool:
    return state.position == level.goal


def successors(level: Level, state: State) -> Iterable[tuple[str, State, int]]:
    for destination in level.graph[state.position]:
        guards = state.active_guards
        if destination in guards:
            guards = frozenset(g for g in guards if g != destination)

        yield destination, State(destination, guards), 1


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
